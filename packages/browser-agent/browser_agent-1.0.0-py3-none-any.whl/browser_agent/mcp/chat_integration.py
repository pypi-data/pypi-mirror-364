"""MCP Chat Integration for one-button MCP functionality in chat interface"""

import asyncio
import threading
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from .server_manager import MCPServerManager
from .types import MCPTool, MCPToolCall, MCPToolResult


class MCPChatIntegration:
    """Integrates MCP functionality into the chat interface"""
    
    def __init__(self, server_manager: MCPServerManager):
        self.server_manager = server_manager
        self.message_callback: Optional[Callable[[str, str], None]] = None
        self.status_callback: Optional[Callable[[str], None]] = None
        
        # MCP command patterns
        self.mcp_commands = {
            "list_tools": self.list_available_tools,
            "list_servers": self.list_connected_servers,
            "call_tool": self.call_tool_interactive,
            "connect_server": self.connect_server_interactive,
            "disconnect_server": self.disconnect_server_interactive,
            "server_status": self.show_server_status,
            "help": self.show_mcp_help
        }
    
    def set_callbacks(self, message_callback: Callable[[str, str], None], 
                     status_callback: Callable[[str], None]):
        """Set callbacks for sending messages and status updates"""
        self.message_callback = message_callback
        self.status_callback = status_callback
    
    def is_mcp_command(self, message: str) -> bool:
        """Check if message is an MCP command"""
        message = message.strip().lower()
        
        # Direct MCP commands
        if message.startswith("/mcp "):
            return True
        
        # Natural language patterns that suggest MCP usage
        mcp_patterns = [
            "use mcp", "call mcp", "mcp tool", "mcp server",
            "list mcp", "show mcp", "connect mcp", "disconnect mcp",
            "available tools", "mcp help", "model context protocol"
        ]
        
        return any(pattern in message for pattern in mcp_patterns)
    
    def process_mcp_message(self, message: str) -> bool:
        """Process MCP-related message and return True if handled"""
        if not self.is_mcp_command(message):
            return False
        
        # Parse command
        command, args = self.parse_mcp_command(message)
        
        if command in self.mcp_commands:
            # Execute command in background thread
            threading.Thread(
                target=self.execute_mcp_command,
                args=(command, args),
                daemon=True
            ).start()
            return True
        
        # Handle natural language MCP requests
        if self.is_natural_mcp_request(message):
            threading.Thread(
                target=self.handle_natural_mcp_request,
                args=(message,),
                daemon=True
            ).start()
            return True
        
        return False
    
    def parse_mcp_command(self, message: str) -> tuple[str, List[str]]:
        """Parse MCP command and arguments"""
        message = message.strip()
        
        # Direct command format: /mcp command args
        if message.startswith("/mcp "):
            parts = message[5:].split()
            command = parts[0] if parts else "help"
            args = parts[1:] if len(parts) > 1 else []
            return command, args
        
        # Natural language parsing
        message_lower = message.lower()
        
        if "list" in message_lower and "tool" in message_lower:
            return "list_tools", []
        elif "list" in message_lower and "server" in message_lower:
            return "list_servers", []
        elif "connect" in message_lower:
            return "connect_server", []
        elif "disconnect" in message_lower:
            return "disconnect_server", []
        elif "status" in message_lower:
            return "server_status", []
        elif "help" in message_lower:
            return "help", []
        else:
            return "help", []
    
    def is_natural_mcp_request(self, message: str) -> bool:
        """Check if message is a natural language MCP request"""
        message_lower = message.lower()
        
        # Look for tool usage patterns
        tool_patterns = [
            "can you", "please", "help me", "i need", "i want",
            "use the", "call the", "run the", "execute"
        ]
        
        # Check if message mentions tools or capabilities
        has_tool_mention = any(pattern in message_lower for pattern in tool_patterns)
        has_mcp_context = any(pattern in message_lower for pattern in [
            "tool", "function", "capability", "service", "api"
        ])
        
        return has_tool_mention and has_mcp_context
    
    def execute_mcp_command(self, command: str, args: List[str]):
        """Execute MCP command"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if command in self.mcp_commands:
                loop.run_until_complete(self.mcp_commands[command](args))
            else:
                self.send_message("assistant", f"Unknown MCP command: {command}")
                
        except Exception as e:
            self.send_message("assistant", f"Error executing MCP command: {str(e)}")
        finally:
            loop.close()
    
    async def list_available_tools(self, args: List[str]):
        """List all available MCP tools"""
        all_tools = self.server_manager.get_all_tools()
        
        if not all_tools:
            self.send_message("assistant", "🔌 No MCP servers connected. Connect to servers first to see available tools.")
            return
        
        message = "🛠️ **Available MCP Tools:**\n\n"
        
        for server_name, tools in all_tools.items():
            if tools:
                message += f"**📦 {server_name}** ({len(tools)} tools):\n"
                for tool in tools:
                    message += f"  • `{tool.name}` - {tool.description}\n"
                message += "\n"
        
        message += "\n💡 **Usage:** Type `/mcp call_tool <tool_name>` or describe what you want to do naturally."
        
        self.send_message("assistant", message)
    
    async def list_connected_servers(self, args: List[str]):
        """List connected MCP servers"""
        connected_servers = self.server_manager.get_connected_servers()
        
        if not connected_servers:
            self.send_message("assistant", "🔌 No MCP servers currently connected.\n\n💡 Go to the MCP tab to connect to servers.")
            return
        
        message = "🔌 **Connected MCP Servers:**\n\n"
        
        for server_name in connected_servers:
            client = self.server_manager.get_client(server_name)
            if client:
                tools_count = len(client.get_available_tools())
                resources_count = len(client.get_available_resources())
                prompts_count = len(client.get_available_prompts())
                
                message += f"• **{server_name}**\n"
                message += f"  - 🛠️ {tools_count} tools\n"
                message += f"  - 📄 {resources_count} resources\n"
                message += f"  - 💬 {prompts_count} prompts\n\n"
        
        self.send_message("assistant", message)
    
    async def call_tool_interactive(self, args: List[str]):
        """Interactive tool calling"""
        if not args:
            # Show available tools for selection
            await self.list_available_tools([])
            self.send_message("assistant", "\n🎯 **To call a tool:** `/mcp call_tool <tool_name> [arguments]`")
            return
        
        tool_name = args[0]
        tool_args = " ".join(args[1:]) if len(args) > 1 else "{}"
        
        # Find the tool
        tool_info = self.find_tool_by_name(tool_name)
        if not tool_info:
            self.send_message("assistant", f"❌ Tool '{tool_name}' not found. Use `/mcp list_tools` to see available tools.")
            return
        
        server_name, tool = tool_info
        
        try:
            # Parse arguments
            if tool_args.strip() == "{}" or not tool_args.strip():
                arguments = {}
            else:
                try:
                    arguments = json.loads(tool_args)
                except json.JSONDecodeError:
                    # Try to parse as simple key=value pairs
                    arguments = self.parse_simple_args(tool_args)
            
            # Create tool call
            tool_call = MCPToolCall(name=tool_name, arguments=arguments)
            
            self.send_message("assistant", f"🔄 Calling tool `{tool_name}` on server `{server_name}`...")
            
            # Call the tool
            result = await self.server_manager.call_tool(server_name, tool_call)
            
            # Format and send result
            self.format_and_send_tool_result(tool_name, result)
            
        except Exception as e:
            self.send_message("assistant", f"❌ Error calling tool '{tool_name}': {str(e)}")
    
    def find_tool_by_name(self, tool_name: str) -> Optional[tuple[str, MCPTool]]:
        """Find a tool by name across all connected servers"""
        all_tools = self.server_manager.get_all_tools()
        
        for server_name, tools in all_tools.items():
            for tool in tools:
                if tool.name == tool_name:
                    return server_name, tool
        
        return None
    
    def parse_simple_args(self, args_str: str) -> Dict[str, Any]:
        """Parse simple key=value arguments"""
        arguments = {}
        
        # Split by spaces, but handle quoted values
        parts = []
        current = ""
        in_quotes = False
        
        for char in args_str:
            if char == '"' and (not current or current[-1] != '\\'):
                in_quotes = not in_quotes
            elif char == ' ' and not in_quotes:
                if current:
                    parts.append(current)
                    current = ""
                continue
            current += char
        
        if current:
            parts.append(current)
        
        # Parse key=value pairs
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                # Remove quotes if present
                value = value.strip('"')
                # Try to convert to appropriate type
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '').isdigit():
                    value = float(value)
                
                arguments[key.strip()] = value
        
        return arguments
    
    def format_and_send_tool_result(self, tool_name: str, result: MCPToolResult):
        """Format and send tool result"""
        if result.isError:
            message = f"❌ **Tool '{tool_name}' failed:**\n\n"
        else:
            message = f"✅ **Tool '{tool_name}' result:**\n\n"
        
        # Format content
        for item in result.content:
            if item.get("type") == "text":
                message += item.get("text", "")
            elif item.get("type") == "image":
                message += f"🖼️ Image: {item.get('data', 'No data')}"
            elif item.get("type") == "resource":
                message += f"📄 Resource: {item.get('resource', 'No resource')}"
            else:
                message += str(item)
            message += "\n"
        
        self.send_message("assistant", message)
    
    async def connect_server_interactive(self, args: List[str]):
        """Interactive server connection"""
        if not args:
            self.send_message("assistant", "🔌 **Connect to MCP Server**\n\nUsage: `/mcp connect_server <server_name>`\n\nGo to the MCP tab to see available servers to connect.")
            return
        
        server_name = args[0]
        
        try:
            self.send_message("assistant", f"🔄 Connecting to server '{server_name}'...")
            
            success = await self.server_manager.connect_server(server_name)
            
            if success:
                client = self.server_manager.get_client(server_name)
                tools_count = len(client.get_available_tools()) if client else 0
                self.send_message("assistant", f"✅ Connected to '{server_name}' successfully!\n🛠️ {tools_count} tools available.")
            else:
                self.send_message("assistant", f"❌ Failed to connect to '{server_name}'. Check if the server is configured correctly.")
                
        except Exception as e:
            self.send_message("assistant", f"❌ Error connecting to '{server_name}': {str(e)}")
    
    async def disconnect_server_interactive(self, args: List[str]):
        """Interactive server disconnection"""
        if not args:
            connected_servers = self.server_manager.get_connected_servers()
            if connected_servers:
                servers_list = ", ".join(connected_servers)
                self.send_message("assistant", f"🔌 **Disconnect from MCP Server**\n\nUsage: `/mcp disconnect_server <server_name>`\n\nConnected servers: {servers_list}")
            else:
                self.send_message("assistant", "🔌 No servers currently connected.")
            return
        
        server_name = args[0]
        
        try:
            self.send_message("assistant", f"🔄 Disconnecting from server '{server_name}'...")
            
            success = await self.server_manager.disconnect_server(server_name)
            
            if success:
                self.send_message("assistant", f"✅ Disconnected from '{server_name}' successfully.")
            else:
                self.send_message("assistant", f"❌ Failed to disconnect from '{server_name}'.")
                
        except Exception as e:
            self.send_message("assistant", f"❌ Error disconnecting from '{server_name}': {str(e)}")
    
    async def show_server_status(self, args: List[str]):
        """Show server status"""
        connected_servers = self.server_manager.get_connected_servers()
        all_servers = self.server_manager.get_all_servers()
        
        message = "🔌 **MCP Server Status:**\n\n"
        
        if not all_servers:
            message += "No MCP servers configured. Go to the MCP tab to add servers.\n"
        else:
            for server in all_servers:
                status_icon = "🟢" if server.name in connected_servers else "🔴" if server.enabled else "⚪"
                status_text = "Connected" if server.name in connected_servers else "Enabled" if server.enabled else "Disabled"
                
                message += f"{status_icon} **{server.name}** - {status_text}\n"
                message += f"   📝 {server.description}\n"
                
                if server.name in connected_servers:
                    client = self.server_manager.get_client(server.name)
                    if client:
                        tools_count = len(client.get_available_tools())
                        message += f"   🛠️ {tools_count} tools available\n"
                
                message += "\n"
        
        self.send_message("assistant", message)
    
    async def show_mcp_help(self, args: List[str]):
        """Show MCP help"""
        help_message = """🔌 **MCP (Model Context Protocol) Help**

**Available Commands:**
• `/mcp list_tools` - Show all available tools
• `/mcp list_servers` - Show connected servers
• `/mcp call_tool <name> [args]` - Call a specific tool
• `/mcp connect_server <name>` - Connect to a server
• `/mcp disconnect_server <name>` - Disconnect from a server
• `/mcp server_status` - Show server status
• `/mcp help` - Show this help

**Natural Language:**
You can also use natural language! Try:
• "List available MCP tools"
• "Show me connected MCP servers"
• "Use the file_read tool to read config.json"
• "Connect to the filesystem server"

**Tool Arguments:**
For simple arguments: `/mcp call_tool file_read path="/path/to/file"`
For JSON arguments: `/mcp call_tool tool_name {"key": "value"}`

**💡 Tips:**
• Go to the MCP tab to browse and install servers
• MCP enables interaction with external tools and services
• Each server provides different capabilities (file system, databases, APIs, etc.)

**🔗 Learn More:**
https://modelcontextprotocol.io/"""
        
        self.send_message("assistant", help_message)
    
    async def handle_natural_mcp_request(self, message: str):
        """Handle natural language MCP requests"""
        message_lower = message.lower()
        
        # Try to understand the intent and suggest appropriate tools
        suggestions = []
        
        # File operations
        if any(word in message_lower for word in ["file", "read", "write", "directory", "folder"]):
            suggestions.append("🗂️ **File Operations**: Try connecting to a filesystem MCP server for file operations.")
        
        # Database operations
        if any(word in message_lower for word in ["database", "sql", "query", "table"]):
            suggestions.append("🗄️ **Database**: Try connecting to a database MCP server for SQL operations.")
        
        # Web operations
        if any(word in message_lower for word in ["web", "http", "api", "request", "url"]):
            suggestions.append("🌐 **Web/API**: Try connecting to a web or HTTP MCP server for API calls.")
        
        # Git operations
        if any(word in message_lower for word in ["git", "repository", "commit", "branch"]):
            suggestions.append("📚 **Git**: Try connecting to a Git MCP server for repository operations.")
        
        if suggestions:
            response = "🤖 I understand you want to use MCP capabilities!\n\n" + "\n".join(suggestions)
            response += "\n\n💡 **Next Steps:**\n"
            response += "1. Go to the MCP tab to install and connect to relevant servers\n"
            response += "2. Use `/mcp list_tools` to see available tools\n"
            response += "3. Call tools directly or describe what you want to do"
        else:
            response = "🤖 I can help you with MCP (Model Context Protocol)!\n\n"
            response += "Use `/mcp help` to see available commands, or go to the MCP tab to browse and install servers."
        
        self.send_message("assistant", response)
    
    def send_message(self, sender: str, content: str):
        """Send message through callback"""
        if self.message_callback:
            self.message_callback(sender, content)
    
    def update_status(self, status: str):
        """Update status through callback"""
        if self.status_callback:
            self.status_callback(status)
    
    def get_mcp_quick_actions(self) -> List[Dict[str, str]]:
        """Get quick action buttons for MCP"""
        return [
            {"text": "🛠️ List Tools", "command": "/mcp list_tools"},
            {"text": "🔌 Servers", "command": "/mcp list_servers"},
            {"text": "📊 Status", "command": "/mcp server_status"},
            {"text": "❓ MCP Help", "command": "/mcp help"}
        ]
    
    def show_mcp_menu(self):
        """Show MCP menu with available options"""
        try:
            import tkinter as tk
            from tkinter import messagebox, simpledialog
            
            # Create a simple menu dialog
            menu_options = [
                "📋 List Available Tools",
                "🔗 Connect to Server",
                "📊 Show MCP Status",
                "🛠️ Call Tool",
                "📁 Browse Resources",
                "⚙️ Manage Servers"
            ]
            
            # Show menu using messagebox
            menu_text = "\n".join([f"{i+1}. {option}" for i, option in enumerate(menu_options)])
            choice = simpledialog.askstring(
                "MCP Menu",
                f"Choose an option:\n\n{menu_text}\n\nEnter number (1-{len(menu_options)}) or type command:",
                initialvalue="1"
            )
            
            if choice:
                if choice.isdigit():
                    choice_num = int(choice) - 1
                    if 0 <= choice_num < len(menu_options):
                        self._handle_menu_choice(choice_num)
                else:
                    # Direct command input
                    if self.message_callback:
                        self.message_callback(choice, "user")
                    self.process_mcp_message(choice)
                    
        except Exception as e:
            if self.message_callback:
                self.message_callback(f"Error showing MCP menu: {str(e)}", "system")
    
    def _handle_menu_choice(self, choice: int):
        """Handle menu choice selection"""
        commands = [
            "/mcp list_tools",
            "/mcp connect",
            "/mcp status",
            "/mcp call_tool",
            "/mcp list_resources",
            "/mcp servers"
        ]
        
        if 0 <= choice < len(commands):
            command = commands[choice]
            if self.message_callback:
                self.message_callback(command, "user")
            self.process_mcp_message(command)
    
    def suggest_tools_for_task(self, task_description: str) -> List[str]:
        """Suggest relevant MCP tools for a given task"""
        task_lower = task_description.lower()
        suggestions = []
        
        all_tools = self.server_manager.get_all_tools()
        
        for server_name, tools in all_tools.items():
            for tool in tools:
                tool_desc_lower = tool.description.lower()
                tool_name_lower = tool.name.lower()
                
                # Simple keyword matching
                if any(word in tool_desc_lower or word in tool_name_lower 
                      for word in task_lower.split()):
                    suggestions.append(f"{server_name}.{tool.name}")
        
        return suggestions[:5]  # Return top 5 suggestions