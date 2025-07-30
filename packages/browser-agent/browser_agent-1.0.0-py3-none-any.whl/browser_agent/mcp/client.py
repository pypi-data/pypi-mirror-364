"""MCP (Model Context Protocol) client implementation"""

import asyncio
import json
import logging
import subprocess
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import asdict

from .types import (
    MCPMessage, MCPMethod, MCPServer, MCPTool, MCPResource, MCPPrompt,
    MCPServerInfo, MCPServerCapabilities, MCPToolCall, MCPToolResult
)

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP client for communicating with MCP servers"""
    
    def __init__(self, server_config: MCPServer):
        self.server_config = server_config
        self.process: Optional[subprocess.Popen] = None
        self.connected = False
        self.server_info: Optional[MCPServerInfo] = None
        self.tools: List[MCPTool] = []
        self.resources: List[MCPResource] = []
        self.prompts: List[MCPPrompt] = []
        self._request_id = 0
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._read_task: Optional[asyncio.Task] = None
        
    def _get_next_id(self) -> str:
        """Get next request ID"""
        self._request_id += 1
        return str(self._request_id)
    
    async def connect(self) -> bool:
        """Connect to MCP server"""
        try:
            # Start the server process
            env = {**self.server_config.env} if self.server_config.env else None
            
            self.process = subprocess.Popen(
                [self.server_config.command] + self.server_config.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                bufsize=0
            )
            
            # Start reading responses
            self._read_task = asyncio.create_task(self._read_responses())
            
            # Initialize the connection
            await self._initialize()
            
            # Load capabilities
            await self._load_capabilities()
            
            self.connected = True
            logger.info(f"Connected to MCP server: {self.server_config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.server_config.name}: {e}")
            await self.disconnect()
            return False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        self.connected = False
        
        # Cancel read task
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
        
        # Close process
        if self.process:
            try:
                self.process.terminate()
                await asyncio.sleep(0.1)
                if self.process.poll() is None:
                    self.process.kill()
            except Exception as e:
                logger.error(f"Error terminating MCP server process: {e}")
            finally:
                self.process = None
        
        # Cancel pending requests
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()
        
        logger.info(f"Disconnected from MCP server: {self.server_config.name}")
    
    async def _read_responses(self):
        """Read responses from server"""
        try:
            while self.process and self.process.stdout:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, self.process.stdout.readline
                )
                
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    message = MCPMessage.from_json(line)
                    await self._handle_message(message)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from MCP server: {e}")
                except Exception as e:
                    logger.error(f"Error handling MCP message: {e}")
                    
        except Exception as e:
            logger.error(f"Error reading from MCP server: {e}")
    
    async def _handle_message(self, message: MCPMessage):
        """Handle incoming message"""
        if message.id and str(message.id) in self._pending_requests:
            # This is a response to a request
            future = self._pending_requests.pop(str(message.id))
            if not future.done():
                if message.error:
                    future.set_exception(Exception(f"MCP Error: {message.error}"))
                else:
                    future.set_result(message.result)
        else:
            # This is a notification or unsolicited message
            logger.debug(f"Received notification: {message.method}")
    
    async def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Send request to server and wait for response"""
        if not self.connected or not self.process:
            raise Exception("Not connected to MCP server")
        
        request_id = self._get_next_id()
        message = MCPMessage(
            id=request_id,
            method=method,
            params=params
        )
        
        # Create future for response
        future = asyncio.Future()
        self._pending_requests[request_id] = future
        
        try:
            # Send request
            json_data = message.to_json() + "\n"
            self.process.stdin.write(json_data)
            self.process.stdin.flush()
            
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=30.0)
            return result
            
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            raise Exception(f"Request timeout for method: {method}")
        except Exception as e:
            self._pending_requests.pop(request_id, None)
            raise e
    
    async def _initialize(self):
        """Initialize connection with server"""
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "Browser Agent",
                "version": "1.0.0"
            }
        }
        
        result = await self._send_request(MCPMethod.INITIALIZE.value, params)
        
        if result:
            self.server_info = MCPServerInfo(
                name=result.get("serverInfo", {}).get("name", self.server_config.name),
                version=result.get("serverInfo", {}).get("version", "unknown"),
                capabilities=MCPServerCapabilities(
                    tools="tools" in result.get("capabilities", {}),
                    resources="resources" in result.get("capabilities", {}),
                    prompts="prompts" in result.get("capabilities", {}),
                    completion="completion" in result.get("capabilities", {})
                )
            )
    
    async def _load_capabilities(self):
        """Load server capabilities"""
        if not self.server_info:
            return
        
        # Load tools
        if self.server_info.capabilities.tools:
            try:
                tools_result = await self._send_request(MCPMethod.LIST_TOOLS.value)
                if tools_result and "tools" in tools_result:
                    self.tools = [
                        MCPTool(
                            name=tool["name"],
                            description=tool["description"]
                        )
                        for tool in tools_result["tools"]
                    ]
            except Exception as e:
                logger.error(f"Failed to load tools: {e}")
        
        # Load resources
        if self.server_info.capabilities.resources:
            try:
                resources_result = await self._send_request(MCPMethod.LIST_RESOURCES.value)
                if resources_result and "resources" in resources_result:
                    self.resources = [
                        MCPResource(
                            uri=resource["uri"],
                            name=resource["name"],
                            description=resource["description"],
                            mimeType=resource.get("mimeType")
                        )
                        for resource in resources_result["resources"]
                    ]
            except Exception as e:
                logger.error(f"Failed to load resources: {e}")
        
        # Load prompts
        if self.server_info.capabilities.prompts:
            try:
                prompts_result = await self._send_request(MCPMethod.LIST_PROMPTS.value)
                if prompts_result and "prompts" in prompts_result:
                    self.prompts = [
                        MCPPrompt(
                            name=prompt["name"],
                            description=prompt["description"]
                        )
                        for prompt in prompts_result["prompts"]
                    ]
            except Exception as e:
                logger.error(f"Failed to load prompts: {e}")
    
    async def call_tool(self, tool_call: MCPToolCall) -> MCPToolResult:
        """Call a tool on the server"""
        if not self.server_info or not self.server_info.capabilities.tools:
            raise Exception("Server does not support tools")
        
        params = {
            "name": tool_call.name,
            "arguments": tool_call.arguments
        }
        
        try:
            result = await self._send_request(MCPMethod.CALL_TOOL.value, params)
            
            return MCPToolResult(
                content=result.get("content", []),
                isError=result.get("isError", False)
            )
            
        except Exception as e:
            return MCPToolResult(
                content=[{"type": "text", "text": f"Error calling tool: {str(e)}"}],
                isError=True
            )
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from the server"""
        if not self.server_info or not self.server_info.capabilities.resources:
            raise Exception("Server does not support resources")
        
        params = {"uri": uri}
        return await self._send_request(MCPMethod.READ_RESOURCE.value, params)
    
    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a prompt from the server"""
        if not self.server_info or not self.server_info.capabilities.prompts:
            raise Exception("Server does not support prompts")
        
        params = {"name": name}
        if arguments:
            params["arguments"] = arguments
        
        return await self._send_request(MCPMethod.GET_PROMPT.value, params)
    
    async def ping(self) -> bool:
        """Ping the server to check if it's alive"""
        try:
            await self._send_request(MCPMethod.PING.value)
            return True
        except Exception:
            return False
    
    def get_available_tools(self) -> List[MCPTool]:
        """Get list of available tools"""
        return self.tools.copy()
    
    def get_available_resources(self) -> List[MCPResource]:
        """Get list of available resources"""
        return self.resources.copy()
    
    def get_available_prompts(self) -> List[MCPPrompt]:
        """Get list of available prompts"""
        return self.prompts.copy()
    
    def is_connected(self) -> bool:
        """Check if connected to server"""
        return self.connected and self.process is not None
    
    def get_server_info(self) -> Optional[MCPServerInfo]:
        """Get server information"""
        return self.server_info