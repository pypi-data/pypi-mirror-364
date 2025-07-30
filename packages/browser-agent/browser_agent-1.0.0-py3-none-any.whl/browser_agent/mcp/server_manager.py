"""MCP Server Manager for handling multiple MCP servers"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from .client import MCPClient
from .types import MCPServer, MCPTool, MCPResource, MCPPrompt, MCPToolCall, MCPToolResult

logger = logging.getLogger(__name__)


class MCPServerManager:
    """Manages multiple MCP servers and their connections"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".browser_agent" / "mcp"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.servers: Dict[str, MCPServer] = {}
        self.clients: Dict[str, MCPClient] = {}
        self.connected_servers: Dict[str, MCPClient] = {}
        
        # Event callbacks
        self.on_server_connected: Optional[Callable[[str, MCPClient], None]] = None
        self.on_server_disconnected: Optional[Callable[[str], None]] = None
        self.on_server_error: Optional[Callable[[str, Exception], None]] = None
        
        # Load server configurations
        self.load_servers()
    
    def load_servers(self):
        """Load server configurations from disk"""
        config_file = self.config_dir / "servers.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    servers_data = json.load(f)
                
                for server_data in servers_data:
                    server = MCPServer.from_dict(server_data)
                    self.servers[server.name] = server
                    
                logger.info(f"Loaded {len(self.servers)} MCP server configurations")
                
            except Exception as e:
                logger.error(f"Failed to load MCP server configurations: {e}")
        else:
            # Create default configuration with some popular MCP servers
            self._create_default_config()
    
    def save_servers(self):
        """Save server configurations to disk"""
        config_file = self.config_dir / "servers.json"
        
        try:
            servers_data = [server.to_dict() for server in self.servers.values()]
            
            with open(config_file, 'w') as f:
                json.dump(servers_data, f, indent=2)
                
            logger.info(f"Saved {len(self.servers)} MCP server configurations")
            
        except Exception as e:
            logger.error(f"Failed to save MCP server configurations: {e}")
    
    def _create_default_config(self):
        """Create default MCP server configurations"""
        default_servers = [
            MCPServer(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                description="File system operations - read, write, create, delete files and directories",
                category="system",
                author="Anthropic",
                tags=["filesystem", "files", "directories"]
            ),
            MCPServer(
                name="brave-search",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-brave-search"],
                env={"BRAVE_API_KEY": ""},
                description="Web search using Brave Search API",
                category="web",
                author="Anthropic",
                tags=["search", "web", "brave"]
            ),
            MCPServer(
                name="github",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
                description="GitHub repository operations - search, read files, create issues",
                category="development",
                author="Anthropic",
                tags=["github", "git", "development"]
            ),
            MCPServer(
                name="postgres",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-postgres"],
                env={"POSTGRES_CONNECTION_STRING": ""},
                description="PostgreSQL database operations",
                category="database",
                author="Anthropic",
                tags=["postgres", "database", "sql"]
            ),
            MCPServer(
                name="sqlite",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-sqlite"],
                description="SQLite database operations",
                category="database",
                author="Anthropic",
                tags=["sqlite", "database", "sql"]
            ),
            MCPServer(
                name="puppeteer",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-puppeteer"],
                description="Web automation using Puppeteer",
                category="automation",
                author="Anthropic",
                tags=["puppeteer", "web", "automation"]
            ),
            MCPServer(
                name="memory",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-memory"],
                description="Persistent memory for conversations",
                category="ai",
                author="Anthropic",
                tags=["memory", "persistence", "ai"]
            ),
            MCPServer(
                name="fetch",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-fetch"],
                description="HTTP requests and web content fetching",
                category="web",
                author="Anthropic",
                tags=["http", "fetch", "web"]
            )
        ]
        
        for server in default_servers:
            self.servers[server.name] = server
        
        self.save_servers()
    
    def add_server(self, server: MCPServer) -> bool:
        """Add a new MCP server"""
        if server.name in self.servers:
            logger.warning(f"Server {server.name} already exists")
            return False
        
        self.servers[server.name] = server
        self.save_servers()
        logger.info(f"Added MCP server: {server.name}")
        return True
    
    def remove_server(self, name: str) -> bool:
        """Remove an MCP server"""
        if name not in self.servers:
            return False
        
        # Disconnect if connected
        if name in self.connected_servers:
            asyncio.create_task(self.disconnect_server(name))
        
        del self.servers[name]
        self.save_servers()
        logger.info(f"Removed MCP server: {name}")
        return True
    
    def update_server(self, server: MCPServer) -> bool:
        """Update an existing MCP server"""
        if server.name not in self.servers:
            return False
        
        # If server is connected and config changed, reconnect
        if server.name in self.connected_servers:
            old_server = self.servers[server.name]
            if (old_server.command != server.command or 
                old_server.args != server.args or 
                old_server.env != server.env):
                asyncio.create_task(self._reconnect_server(server.name, server))
        
        self.servers[server.name] = server
        self.save_servers()
        logger.info(f"Updated MCP server: {server.name}")
        return True
    
    async def _reconnect_server(self, name: str, new_config: MCPServer):
        """Reconnect server with new configuration"""
        await self.disconnect_server(name)
        self.servers[name] = new_config
        if new_config.enabled:
            await self.connect_server(name)
    
    def get_server(self, name: str) -> Optional[MCPServer]:
        """Get server configuration"""
        return self.servers.get(name)
    
    def get_all_servers(self) -> List[MCPServer]:
        """Get all server configurations"""
        return list(self.servers.values())
    
    def get_servers_by_category(self, category: str) -> List[MCPServer]:
        """Get servers by category"""
        return [server for server in self.servers.values() if server.category == category]
    
    def search_servers(self, query: str) -> List[MCPServer]:
        """Search servers by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for server in self.servers.values():
            if (query_lower in server.name.lower() or 
                query_lower in server.description.lower() or 
                any(query_lower in tag.lower() for tag in server.tags)):
                results.append(server)
        
        return results
    
    async def connect_server(self, name: str) -> bool:
        """Connect to an MCP server"""
        if name not in self.servers:
            logger.error(f"Server {name} not found")
            return False
        
        if name in self.connected_servers:
            logger.warning(f"Server {name} already connected")
            return True
        
        server = self.servers[name]
        client = MCPClient(server)
        
        try:
            success = await client.connect()
            if success:
                self.connected_servers[name] = client
                server.enabled = True
                self.save_servers()
                
                if self.on_server_connected:
                    self.on_server_connected(name, client)
                
                logger.info(f"Connected to MCP server: {name}")
                return True
            else:
                logger.error(f"Failed to connect to MCP server: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to MCP server {name}: {e}")
            if self.on_server_error:
                self.on_server_error(name, e)
            return False
    
    async def disconnect_server(self, name: str) -> bool:
        """Disconnect from an MCP server"""
        if name not in self.connected_servers:
            return False
        
        client = self.connected_servers.pop(name)
        
        try:
            await client.disconnect()
            
            if name in self.servers:
                self.servers[name].enabled = False
                self.save_servers()
            
            if self.on_server_disconnected:
                self.on_server_disconnected(name)
            
            logger.info(f"Disconnected from MCP server: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server {name}: {e}")
            return False
    
    async def connect_all_enabled(self):
        """Connect to all enabled servers"""
        tasks = []
        for server in self.servers.values():
            if server.enabled and server.name not in self.connected_servers:
                tasks.append(self.connect_server(server.name))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def disconnect_all(self):
        """Disconnect from all servers"""
        tasks = []
        for name in list(self.connected_servers.keys()):
            tasks.append(self.disconnect_server(name))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_connected_servers(self) -> List[str]:
        """Get list of connected server names"""
        return list(self.connected_servers.keys())
    
    def is_server_connected(self, name: str) -> bool:
        """Check if server is connected"""
        return name in self.connected_servers
    
    def get_client(self, name: str) -> Optional[MCPClient]:
        """Get client for connected server"""
        return self.connected_servers.get(name)
    
    async def call_tool(self, server_name: str, tool_call: MCPToolCall) -> MCPToolResult:
        """Call a tool on a specific server"""
        if server_name not in self.connected_servers:
            return MCPToolResult(
                content=[{"type": "text", "text": f"Server {server_name} not connected"}],
                isError=True
            )
        
        client = self.connected_servers[server_name]
        return await client.call_tool(tool_call)
    
    def get_all_tools(self) -> Dict[str, List[MCPTool]]:
        """Get all tools from all connected servers"""
        tools = {}
        for name, client in self.connected_servers.items():
            tools[name] = client.get_available_tools()
        return tools
    
    def get_all_resources(self) -> Dict[str, List[MCPResource]]:
        """Get all resources from all connected servers"""
        resources = {}
        for name, client in self.connected_servers.items():
            resources[name] = client.get_available_resources()
        return resources
    
    def get_all_prompts(self) -> Dict[str, List[MCPPrompt]]:
        """Get all prompts from all connected servers"""
        prompts = {}
        for name, client in self.connected_servers.items():
            prompts[name] = client.get_available_prompts()
        return prompts
    
    def find_tool(self, tool_name: str) -> Optional[tuple[str, MCPTool]]:
        """Find a tool by name across all connected servers"""
        for server_name, client in self.connected_servers.items():
            for tool in client.get_available_tools():
                if tool.name == tool_name:
                    return (server_name, tool)
        return None
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all connected servers"""
        results = {}
        tasks = []
        
        for name, client in self.connected_servers.items():
            tasks.append(self._check_server_health(name, client))
        
        if tasks:
            health_results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, (name, _) in enumerate(self.connected_servers.items()):
                results[name] = not isinstance(health_results[i], Exception) and health_results[i]
        
        return results
    
    async def _check_server_health(self, name: str, client: MCPClient) -> bool:
        """Check health of a single server"""
        try:
            return await client.ping()
        except Exception as e:
            logger.warning(f"Health check failed for server {name}: {e}")
            return False