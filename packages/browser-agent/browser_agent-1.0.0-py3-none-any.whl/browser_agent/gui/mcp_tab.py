"""MCP (Model Context Protocol) GUI tab for managing MCP servers and marketplace"""

import tkinter as tk
import customtkinter as ctk
import asyncio
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..mcp.server_manager import MCPServerManager
from ..mcp.marketplace import MCPMarketplace
from ..mcp.types import MCPServer, MCPTool, MCPToolCall, MCPToolResult


class MCPTab:
    """MCP management tab for the GUI"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        # Initialize MCP components
        self.server_manager = MCPServerManager()
        self.marketplace = MCPMarketplace(self.server_manager)
        
        # GUI state
        self.selected_server = None
        self.current_view = "marketplace"  # marketplace, installed, tools
        
        self.create_widgets()
        self.setup_layout()
        
        # Start background tasks
        self.start_background_tasks()
    
    def create_widgets(self):
        """Create MCP tab widgets"""
        # Main container
        self.main_container = ctk.CTkFrame(self.parent)
        
        # Header with navigation
        self.header_frame = ctk.CTkFrame(self.main_container)
        self.create_header()
        
        # Content area
        self.content_frame = ctk.CTkFrame(self.main_container)
        
        # Create different views
        self.create_marketplace_view()
        self.create_installed_view()
        self.create_tools_view()
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self.main_container, height=30)
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="🔌 MCP Ready - 0 servers connected",
            font=ctk.CTkFont(size=11)
        )
    
    def create_header(self):
        """Create header with navigation buttons"""
        # Title
        title_label = ctk.CTkLabel(
            self.header_frame,
            text="🔌 MCP (Model Context Protocol)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        nav_frame.pack(side="left", padx=20, pady=15)
        
        self.marketplace_btn = ctk.CTkButton(
            nav_frame,
            text="🏪 Marketplace",
            command=lambda: self.switch_view("marketplace"),
            width=120,
            height=35
        )
        self.marketplace_btn.pack(side="left", padx=5)
        
        self.installed_btn = ctk.CTkButton(
            nav_frame,
            text="📦 Installed",
            command=lambda: self.switch_view("installed"),
            width=120,
            height=35,
            fg_color="#666666"
        )
        self.installed_btn.pack(side="left", padx=5)
        
        self.tools_btn = ctk.CTkButton(
            nav_frame,
            text="🛠️ Tools",
            command=lambda: self.switch_view("tools"),
            width=120,
            height=35,
            fg_color="#666666"
        )
        self.tools_btn.pack(side="left", padx=5)
        
        # Action buttons
        action_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        action_frame.pack(side="right", padx=20, pady=15)
        
        self.refresh_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Refresh",
            command=self.refresh_marketplace,
            width=100,
            height=35
        )
        self.refresh_btn.pack(side="right", padx=5)
        
        self.connect_all_btn = ctk.CTkButton(
            action_frame,
            text="🔗 Connect All",
            command=self.connect_all_servers,
            width=120,
            height=35,
            fg_color="#2fa572"
        )
        self.connect_all_btn.pack(side="right", padx=5)
    
    def create_marketplace_view(self):
        """Create marketplace view"""
        self.marketplace_frame = ctk.CTkFrame(self.content_frame)
        
        # Search and filters
        search_frame = ctk.CTkFrame(self.marketplace_frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search MCP servers...",
            width=300
        )
        self.search_entry.pack(side="left", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search_changed)
        
        # Category filter
        self.category_var = ctk.StringVar(value="All Categories")
        self.category_dropdown = ctk.CTkOptionMenu(
            search_frame,
            variable=self.category_var,
            values=["All Categories"],
            command=self.on_category_changed,
            width=150
        )
        self.category_dropdown.pack(side="left", padx=10, pady=10)
        
        # Server list
        self.marketplace_list_frame = ctk.CTkScrollableFrame(
            self.marketplace_frame,
            label_text="Available MCP Servers"
        )
        self.marketplace_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_installed_view(self):
        """Create installed servers view"""
        self.installed_frame = ctk.CTkFrame(self.content_frame)
        
        # Installed servers list
        self.installed_list_frame = ctk.CTkScrollableFrame(
            self.installed_frame,
            label_text="Installed MCP Servers"
        )
        self.installed_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_tools_view(self):
        """Create tools view"""
        self.tools_frame = ctk.CTkFrame(self.content_frame)
        
        # Tools list
        self.tools_list_frame = ctk.CTkScrollableFrame(
            self.tools_frame,
            label_text="Available MCP Tools"
        )
        self.tools_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_layout(self):
        """Setup the layout"""
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.content_frame.pack(fill="both", expand=True, pady=(0, 10))
        self.status_frame.pack(fill="x")
        self.status_frame.pack_propagate(False)
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Show marketplace view by default
        self.switch_view("marketplace")
    
    def switch_view(self, view: str):
        """Switch between different views"""
        # Hide all views
        self.marketplace_frame.pack_forget()
        self.installed_frame.pack_forget()
        self.tools_frame.pack_forget()
        
        # Reset button colors
        self.marketplace_btn.configure(fg_color="#666666")
        self.installed_btn.configure(fg_color="#666666")
        self.tools_btn.configure(fg_color="#666666")
        
        # Show selected view
        if view == "marketplace":
            self.marketplace_frame.pack(fill="both", expand=True)
            self.marketplace_btn.configure(fg_color="#1f538d")
            self.refresh_marketplace_list()
        elif view == "installed":
            self.installed_frame.pack(fill="both", expand=True)
            self.installed_btn.configure(fg_color="#1f538d")
            self.refresh_installed_list()
        elif view == "tools":
            self.tools_frame.pack(fill="both", expand=True)
            self.tools_btn.configure(fg_color="#1f538d")
            self.refresh_tools_list()
        
        self.current_view = view
    
    def refresh_marketplace_list(self):
        """Refresh marketplace server list"""
        # Clear existing items
        for widget in self.marketplace_list_frame.winfo_children():
            widget.destroy()
        
        # Get servers to display
        query = self.search_entry.get().strip()
        category = self.category_var.get()
        
        if query:
            servers = self.marketplace.search_servers(query)
        elif category != "All Categories":
            servers = self.marketplace.get_servers_by_category(category)
        else:
            servers = self.marketplace.get_available_servers()
        
        # Create server cards
        for server in servers:
            self.create_marketplace_server_card(server)
        
        # Update category dropdown
        categories = ["All Categories"] + self.marketplace.get_categories()
        self.category_dropdown.configure(values=categories)
    
    def create_marketplace_server_card(self, server: MCPServer):
        """Create a server card for marketplace"""
        card_frame = ctk.CTkFrame(self.marketplace_list_frame)
        card_frame.pack(fill="x", padx=5, pady=5)
        
        # Server info
        info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Name and category
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"📦 {server.name}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w")
        
        category_label = ctk.CTkLabel(
            info_frame,
            text=f"Category: {server.category} | Version: {server.version}",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        category_label.pack(anchor="w")
        
        # Description
        desc_label = ctk.CTkLabel(
            info_frame,
            text=server.description[:100] + "..." if len(server.description) > 100 else server.description,
            font=ctk.CTkFont(size=11),
            wraplength=400
        )
        desc_label.pack(anchor="w", pady=(5, 0))
        
        # Tags
        if server.tags:
            tags_text = " ".join([f"#{tag}" for tag in server.tags[:5]])
            tags_label = ctk.CTkLabel(
                info_frame,
                text=tags_text,
                font=ctk.CTkFont(size=9),
                text_color="#4CAF50"
            )
            tags_label.pack(anchor="w", pady=(2, 0))
        
        # Action buttons
        action_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        action_frame.pack(side="right", padx=10, pady=10)
        
        # Check if installed
        is_installed = self.marketplace.is_server_installed(server.name)
        is_enabled = self.marketplace.is_server_enabled(server.name)
        
        if not is_installed:
            install_btn = ctk.CTkButton(
                action_frame,
                text="📥 Install",
                command=lambda s=server: self.install_server(s),
                width=80,
                height=30,
                fg_color="#2fa572"
            )
            install_btn.pack(pady=2)
        else:
            if is_enabled:
                disable_btn = ctk.CTkButton(
                    action_frame,
                    text="⏸️ Disable",
                    command=lambda s=server: self.disable_server(s.name),
                    width=80,
                    height=30,
                    fg_color="#ff8800"
                )
                disable_btn.pack(pady=2)
            else:
                enable_btn = ctk.CTkButton(
                    action_frame,
                    text="▶️ Enable",
                    command=lambda s=server: self.enable_server(s.name),
                    width=80,
                    height=30,
                    fg_color="#2fa572"
                )
                enable_btn.pack(pady=2)
            
            uninstall_btn = ctk.CTkButton(
                action_frame,
                text="🗑️ Remove",
                command=lambda s=server: self.uninstall_server(s.name),
                width=80,
                height=30,
                fg_color="#e74c3c"
            )
            uninstall_btn.pack(pady=2)
    
    def refresh_installed_list(self):
        """Refresh installed servers list"""
        # Clear existing items
        for widget in self.installed_list_frame.winfo_children():
            widget.destroy()
        
        installed_servers = self.marketplace.get_installed_servers()
        
        for server in installed_servers:
            self.create_installed_server_card(server)
    
    def create_installed_server_card(self, server: MCPServer):
        """Create a server card for installed servers"""
        card_frame = ctk.CTkFrame(self.installed_list_frame)
        card_frame.pack(fill="x", padx=5, pady=5)
        
        # Server info
        info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Status indicator
        is_connected = self.server_manager.is_server_connected(server.name)
        status_icon = "🟢" if is_connected else "🔴" if server.enabled else "⚪"
        status_text = "Connected" if is_connected else "Enabled" if server.enabled else "Disabled"
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"{status_icon} {server.name} ({status_text})",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w")
        
        # Description
        desc_label = ctk.CTkLabel(
            info_frame,
            text=server.description,
            font=ctk.CTkFont(size=11),
            wraplength=400
        )
        desc_label.pack(anchor="w", pady=(5, 0))
        
        # Tools count
        if is_connected:
            client = self.server_manager.get_client(server.name)
            if client:
                tools_count = len(client.get_available_tools())
                tools_label = ctk.CTkLabel(
                    info_frame,
                    text=f"🛠️ {tools_count} tools available",
                    font=ctk.CTkFont(size=10),
                    text_color="#4CAF50"
                )
                tools_label.pack(anchor="w", pady=(2, 0))
        
        # Action buttons
        action_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        action_frame.pack(side="right", padx=10, pady=10)
        
        if server.enabled and not is_connected:
            connect_btn = ctk.CTkButton(
                action_frame,
                text="🔗 Connect",
                command=lambda s=server: self.connect_server(s.name),
                width=80,
                height=30,
                fg_color="#2fa572"
            )
            connect_btn.pack(pady=2)
        elif is_connected:
            disconnect_btn = ctk.CTkButton(
                action_frame,
                text="🔌 Disconnect",
                command=lambda s=server: self.disconnect_server(s.name),
                width=80,
                height=30,
                fg_color="#ff8800"
            )
            disconnect_btn.pack(pady=2)
        
        if not server.enabled:
            enable_btn = ctk.CTkButton(
                action_frame,
                text="▶️ Enable",
                command=lambda s=server: self.enable_server(s.name),
                width=80,
                height=30,
                fg_color="#2fa572"
            )
            enable_btn.pack(pady=2)
        else:
            disable_btn = ctk.CTkButton(
                action_frame,
                text="⏸️ Disable",
                command=lambda s=server: self.disable_server(s.name),
                width=80,
                height=30,
                fg_color="#ff8800"
            )
            disable_btn.pack(pady=2)
        
        # Add edit button for servers with environment variables
        if server.env:
            edit_btn = ctk.CTkButton(
                action_frame,
                text="⚙️ Config",
                command=lambda s=server: self.edit_server_config(s.name),
                width=100,
                height=30,
                fg_color="#1f538d"
            )
            edit_btn.pack(pady=2)
    
    def refresh_tools_list(self):
        """Refresh tools list"""
        # Clear existing items
        for widget in self.tools_list_frame.winfo_children():
            widget.destroy()
        
        all_tools = self.server_manager.get_all_tools()
        
        for server_name, tools in all_tools.items():
            if tools:
                # Server header
                server_header = ctk.CTkLabel(
                    self.tools_list_frame,
                    text=f"🔌 {server_name} ({len(tools)} tools)",
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                server_header.pack(anchor="w", padx=10, pady=(10, 5))
                
                # Tools
                for tool in tools:
                    self.create_tool_card(server_name, tool)
    
    def create_tool_card(self, server_name: str, tool: MCPTool):
        """Create a tool card"""
        card_frame = ctk.CTkFrame(self.tools_list_frame)
        card_frame.pack(fill="x", padx=5, pady=2)
        
        # Tool info
        info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"🛠️ {tool.name}",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        name_label.pack(anchor="w")
        
        desc_label = ctk.CTkLabel(
            info_frame,
            text=tool.description,
            font=ctk.CTkFont(size=10),
            wraplength=400
        )
        desc_label.pack(anchor="w")
        
        # Test button
        test_btn = ctk.CTkButton(
            card_frame,
            text="🧪 Test",
            command=lambda s=server_name, t=tool: self.test_tool(s, t),
            width=60,
            height=25,
            fg_color="#666666"
        )
        test_btn.pack(side="right", padx=10, pady=5)
    
    def on_search_changed(self, event=None):
        """Handle search text change"""
        if self.current_view == "marketplace":
            self.refresh_marketplace_list()
    
    def on_category_changed(self, category: str):
        """Handle category selection change"""
        if self.current_view == "marketplace":
            self.refresh_marketplace_list()
    
    def install_server(self, server: MCPServer):
        """Install a server"""
        def install_worker():
            success = self.marketplace.install_server(server.name)
            self.main_window.root.after(0, lambda: self.on_install_complete(server.name, success))
        
        threading.Thread(target=install_worker, daemon=True).start()
        self.update_status(f"Installing {server.name}...")
    
    def on_install_complete(self, server_name: str, success: bool):
        """Handle install completion"""
        if success:
            self.update_status(f"✅ {server_name} installed successfully")
            self.refresh_marketplace_list()
            self.refresh_installed_list()
        else:
            self.update_status(f"❌ Failed to install {server_name}")
    
    def uninstall_server(self, server_name: str):
        """Uninstall a server"""
        def uninstall_worker():
            success = self.marketplace.uninstall_server(server_name)
            self.main_window.root.after(0, lambda: self.on_uninstall_complete(server_name, success))
        
        threading.Thread(target=uninstall_worker, daemon=True).start()
        self.update_status(f"Uninstalling {server_name}...")
    
    def on_uninstall_complete(self, server_name: str, success: bool):
        """Handle uninstall completion"""
        if success:
            self.update_status(f"✅ {server_name} uninstalled successfully")
            self.refresh_marketplace_list()
            self.refresh_installed_list()
        else:
            self.update_status(f"❌ Failed to uninstall {server_name}")
    
    def enable_server(self, server_name: str):
        """Enable a server"""
        # Check if server requires authentication tokens
        server = self.server_manager.get_server(server_name)
        if server and server.env:
            # Check for empty environment variables that might need tokens
            missing_tokens = []
            for key, value in server.env.items():
                if not value and any(token_keyword in key.lower() for token_keyword in ['api_key', 'token', 'key', 'secret', 'password', 'connection']):
                    missing_tokens.append(key)
            
            if missing_tokens:
                self._prompt_for_tokens(server_name, missing_tokens)
                return
        
        # Proceed with normal enabling if no tokens needed
        self._enable_server_worker(server_name)
    
    def _prompt_for_tokens(self, server_name: str, missing_tokens: list):
        """Prompt user for authentication tokens"""
        dialog = ctk.CTkToplevel(self.main_window.root)
        dialog.title(f"Authentication Required - {server_name}")
        dialog.geometry("500x400")
        dialog.transient(self.main_window.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header_label = ctk.CTkLabel(
            dialog,
            text=f"🔐 {server_name} requires authentication",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(pady=20)
        
        info_label = ctk.CTkLabel(
            dialog,
            text="Please provide the required API tokens/keys to enable this server:",
            font=ctk.CTkFont(size=12),
            wraplength=450
        )
        info_label.pack(pady=(0, 20))
        
        # Token entries
        token_entries = {}
        for token_key in missing_tokens:
            token_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            token_frame.pack(fill="x", padx=20, pady=5)
            
            token_label = ctk.CTkLabel(
                token_frame,
                text=f"{token_key}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=200
            )
            token_label.pack(side="left", padx=(0, 10))
            
            token_entry = ctk.CTkEntry(
                token_frame,
                placeholder_text=f"Enter your {token_key.lower()}",
                show="*" if any(secret in token_key.lower() for secret in ['secret', 'password']) else None,
                width=250
            )
            token_entry.pack(side="right", fill="x", expand=True)
            token_entries[token_key] = token_entry
        
        # Instructions
        instructions_frame = ctk.CTkFrame(dialog)
        instructions_frame.pack(fill="x", padx=20, pady=20)
        
        instructions_text = self._get_token_instructions(server_name)
        if instructions_text:
            instructions_label = ctk.CTkLabel(
                instructions_frame,
                text=f"💡 How to get your tokens:\n{instructions_text}",
                font=ctk.CTkFont(size=11),
                wraplength=450,
                justify="left"
            )
            instructions_label.pack(padx=15, pady=15)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def save_and_enable():
            # Update server environment variables
            server = self.server_manager.get_server(server_name)
            if server:
                for token_key, entry in token_entries.items():
                    token_value = entry.get().strip()
                    if token_value:
                        server.env[token_key] = token_value
                
                self.server_manager.update_server(server)
                dialog.destroy()
                self._enable_server_worker(server_name)
            else:
                self.update_status(f"❌ Server {server_name} not found")
                dialog.destroy()
        
        def cancel():
            dialog.destroy()
            self.update_status(f"❌ Authentication cancelled for {server_name}")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=cancel,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save & Enable",
            command=save_and_enable
        )
        save_btn.pack(side="right", padx=5)
        
        # Focus on first entry
        if token_entries:
            first_entry = list(token_entries.values())[0]
            first_entry.focus()
    
    def _get_token_instructions(self, server_name: str) -> str:
        """Get instructions for obtaining tokens for specific servers"""
        instructions = {
            "brave-search": "Visit https://api.search.brave.com/app/keys to get your Brave Search API key",
            "github": "Go to GitHub Settings > Developer settings > Personal access tokens > Generate new token",
            "postgres": "Use format: postgresql://username:password@host:port/database",
            "openai": "Get your API key from https://platform.openai.com/api-keys",
            "anthropic": "Get your API key from https://console.anthropic.com/",
            "google": "Get your API key from Google Cloud Console or AI Studio",
            "slack": "Create a Slack app at https://api.slack.com/apps and get the bot token",
            "notion": "Create an integration at https://www.notion.so/my-integrations",
            "filesystem": "No API key required - configure allowed directories",
            "sqlite": "No API key required - configure database path",
            "puppeteer": "No API key required - browser automation tool",
            "memory": "No API key required - local memory storage",
        }
        return instructions.get(server_name, "Check the server documentation for token requirements")
    
    def _enable_server_worker(self, server_name: str):
        """Worker method to enable server"""
        def enable_worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.marketplace.enable_server(server_name))
            self.main_window.root.after(0, lambda: self.on_enable_complete(server_name, success))
        
        threading.Thread(target=enable_worker, daemon=True).start()
        self.update_status(f"Enabling {server_name}...")
    
    def on_enable_complete(self, server_name: str, success: bool):
        """Handle enable completion"""
        if success:
            self.update_status(f"✅ {server_name} enabled and connected")
        else:
            self.update_status(f"❌ Failed to enable {server_name}")
        
        self.refresh_marketplace_list()
        self.refresh_installed_list()
        self.update_connection_status()
    
    def disable_server(self, server_name: str):
        """Disable a server"""
        def disable_worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.marketplace.disable_server(server_name))
            self.main_window.root.after(0, lambda: self.on_disable_complete(server_name, success))
        
        threading.Thread(target=disable_worker, daemon=True).start()
        self.update_status(f"Disabling {server_name}...")
    
    def on_disable_complete(self, server_name: str, success: bool):
        """Handle disable completion"""
        if success:
            self.update_status(f"✅ {server_name} disabled")
        else:
            self.update_status(f"❌ Failed to disable {server_name}")
        
        self.refresh_marketplace_list()
        self.refresh_installed_list()
        self.update_connection_status()
    
    def connect_server(self, server_name: str):
        """Connect to a server"""
        def connect_worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.server_manager.connect_server(server_name))
            self.main_window.root.after(0, lambda: self.on_connect_complete(server_name, success))
        
        threading.Thread(target=connect_worker, daemon=True).start()
        self.update_status(f"Connecting to {server_name}...")
    
    def on_connect_complete(self, server_name: str, success: bool):
        """Handle connect completion"""
        if success:
            self.update_status(f"✅ Connected to {server_name}")
        else:
            self.update_status(f"❌ Failed to connect to {server_name}")
        
        self.refresh_installed_list()
        self.update_connection_status()
    
    def disconnect_server(self, server_name: str):
        """Disconnect from a server"""
        def disconnect_worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.server_manager.disconnect_server(server_name))
            self.main_window.root.after(0, lambda: self.on_disconnect_complete(server_name, success))
        
        threading.Thread(target=disconnect_worker, daemon=True).start()
        self.update_status(f"Disconnecting from {server_name}...")
    
    def on_disconnect_complete(self, server_name: str, success: bool):
        """Handle disconnect completion"""
        if success:
            self.update_status(f"✅ Disconnected from {server_name}")
        else:
            self.update_status(f"❌ Failed to disconnect from {server_name}")
        
        self.refresh_installed_list()
        self.update_connection_status()
    
    def connect_all_servers(self):
        """Connect to all enabled servers"""
        def connect_all_worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.server_manager.connect_all_enabled())
            self.main_window.root.after(0, self.on_connect_all_complete)
        
        threading.Thread(target=connect_all_worker, daemon=True).start()
        self.update_status("Connecting to all enabled servers...")
    
    def on_connect_all_complete(self):
        """Handle connect all completion"""
        connected_count = len(self.server_manager.get_connected_servers())
        self.update_status(f"✅ Connected to {connected_count} servers")
        self.refresh_installed_list()
        self.update_connection_status()
    
    def refresh_marketplace(self):
        """Refresh marketplace data"""
        def refresh_worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.marketplace.refresh_marketplace())
            self.main_window.root.after(0, lambda: self.on_refresh_complete(success))
        
        threading.Thread(target=refresh_worker, daemon=True).start()
        self.update_status("Refreshing marketplace...")
    
    def on_refresh_complete(self, success: bool):
        """Handle refresh completion"""
        if success:
            self.update_status("✅ Marketplace refreshed")
            self.refresh_marketplace_list()
        else:
            self.update_status("❌ Failed to refresh marketplace")
    
    def test_tool(self, server_name: str, tool: MCPTool):
        """Test a tool"""
        # Create a simple test dialog
        dialog = ctk.CTkToplevel(self.main_window.root)
        dialog.title(f"Test Tool: {tool.name}")
        dialog.geometry("400x300")
        dialog.transient(self.main_window.root)
        dialog.grab_set()
        
        # Tool info
        info_label = ctk.CTkLabel(
            dialog,
            text=f"Tool: {tool.name}\nServer: {server_name}\n\nDescription: {tool.description}",
            font=ctk.CTkFont(size=12),
            wraplength=350
        )
        info_label.pack(padx=20, pady=20)
        
        # Arguments entry (simplified)
        args_label = ctk.CTkLabel(dialog, text="Arguments (JSON):")
        args_label.pack(padx=20, pady=(0, 5))
        
        args_entry = ctk.CTkTextbox(dialog, height=100)
        args_entry.pack(padx=20, pady=(0, 10), fill="x")
        args_entry.insert("1.0", "{}")
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        def run_test():
            try:
                import json
                args = json.loads(args_entry.get("1.0", "end-1c"))
                tool_call = MCPToolCall(name=tool.name, arguments=args)
                
                def test_worker():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self.server_manager.call_tool(server_name, tool_call))
                    dialog.after(0, lambda: show_result(result))
                
                threading.Thread(target=test_worker, daemon=True).start()
                
            except Exception as e:
                show_result(MCPToolResult(
                    content=[{"type": "text", "text": f"Error: {str(e)}"}],
                    isError=True
                ))
        
        def show_result(result: MCPToolResult):
            result_text = "\n".join([item.get("text", str(item)) for item in result.content])
            
            result_dialog = ctk.CTkToplevel(dialog)
            result_dialog.title("Tool Result")
            result_dialog.geometry("500x400")
            
            result_textbox = ctk.CTkTextbox(result_dialog)
            result_textbox.pack(fill="both", expand=True, padx=20, pady=20)
            result_textbox.insert("1.0", result_text)
            result_textbox.configure(state="disabled")
        
        test_btn = ctk.CTkButton(
            button_frame,
            text="🧪 Run Test",
            command=run_test
        )
        test_btn.pack(side="right", padx=5)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=dialog.destroy,
            fg_color="#666666"
        )
        close_btn.pack(side="right", padx=5)
    
    def update_status(self, message: str):
        """Update status message"""
        self.status_label.configure(text=message)
        # Auto-clear status after 5 seconds
        self.main_window.root.after(5000, self.update_connection_status)
    
    def update_connection_status(self):
        """Update connection status"""
        connected_count = len(self.server_manager.get_connected_servers())
        self.status_label.configure(text=f"🔌 MCP Ready - {connected_count} servers connected")
    
    def start_background_tasks(self):
        """Start background tasks"""
        # Auto-refresh marketplace on startup
        def startup_refresh():
            self.main_window.root.after(1000, self.refresh_marketplace)
        
        startup_refresh()
        
        # Update connection status periodically
        def periodic_update():
            self.update_connection_status()
            self.main_window.root.after(10000, periodic_update)  # Every 10 seconds
        
        periodic_update()
    
    def get_server_manager(self) -> MCPServerManager:
        """Get the server manager instance"""
        return self.server_manager
    
    def edit_server_config(self, server_name: str):
        """Edit server configuration (environment variables)"""
        server = self.server_manager.get_server(server_name)
        if not server or not server.env:
            self.update_status(f"❌ No configuration available for {server_name}")
            return
        
        dialog = ctk.CTkToplevel(self.main_window.root)
        dialog.title(f"Configure {server_name}")
        dialog.geometry("600x500")
        dialog.transient(self.main_window.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header_label = ctk.CTkLabel(
            dialog,
            text=f"⚙️ Configure {server_name}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(pady=20)
        
        info_label = ctk.CTkLabel(
            dialog,
            text="Update environment variables and configuration:",
            font=ctk.CTkFont(size=12),
            wraplength=550
        )
        info_label.pack(pady=(0, 20))
        
        # Scrollable frame for environment variables
        env_frame = ctk.CTkScrollableFrame(
            dialog,
            label_text="Environment Variables",
            height=300
        )
        env_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Environment variable entries
        env_entries = {}
        for key, value in server.env.items():
            var_frame = ctk.CTkFrame(env_frame, fg_color="transparent")
            var_frame.pack(fill="x", pady=5)
            
            var_label = ctk.CTkLabel(
                var_frame,
                text=f"{key}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=200
            )
            var_label.pack(side="left", padx=(0, 10))
            
            # Determine if this should be a password field
            is_secret = any(secret in key.lower() for secret in ['secret', 'password', 'key', 'token'])
            
            var_entry = ctk.CTkEntry(
                var_frame,
                placeholder_text=f"Enter {key.lower()}",
                show="*" if is_secret else None,
                width=300
            )
            var_entry.pack(side="right", fill="x", expand=True)
            
            # Set current value
            if value:
                var_entry.insert(0, value)
            
            env_entries[key] = var_entry
        
        # Instructions
        instructions_text = self._get_token_instructions(server_name)
        if instructions_text:
            instructions_frame = ctk.CTkFrame(dialog)
            instructions_frame.pack(fill="x", padx=20, pady=10)
            
            instructions_label = ctk.CTkLabel(
                instructions_frame,
                text=f"💡 {instructions_text}",
                font=ctk.CTkFont(size=11),
                wraplength=550,
                justify="left"
            )
            instructions_label.pack(padx=15, pady=15)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def save_config():
            # Update server environment variables
            for key, entry in env_entries.items():
                new_value = entry.get().strip()
                server.env[key] = new_value
            
            self.server_manager.update_server(server)
            dialog.destroy()
            self.update_status(f"✅ Configuration updated for {server_name}")
            
            # Refresh views
            self.refresh_installed_list()
        
        def cancel():
            dialog.destroy()
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=cancel,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Configuration",
            command=save_config
        )
        save_btn.pack(side="right", padx=5)
        
        # Focus on first entry
        if env_entries:
            first_entry = list(env_entries.values())[0]
            first_entry.focus()
    
    def get_marketplace(self) -> MCPMarketplace:
        """Get the marketplace instance"""
        return self.marketplace