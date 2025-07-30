import tkinter as tk
import customtkinter as ctk
import asyncio
import threading
from typing import Dict, Any, Optional
from datetime import datetime
import json

from .chat_interface import ChatInterface
from .settings_tab import SettingsTab
from .brain_tab import BrainTab
from .enhanced_browser_tab import EnhancedBrowserTab
from .desktop_automation_tab import DesktopAutomationTab
from .task_log_tab import TaskLogTab
from .mcp_tab import MCPTab
from ..core.config import Config
from ..core.agent import BrowserAgent
from ..core.multi_llm_processor import MultiLLMProcessor, LLMProvider
from ..browsers.manager import BrowserManager
from ..mcp.server_manager import MCPServerManager
from ..mcp.chat_integration import MCPChatIntegration


class MainWindow:
    """Main GUI window for Browser Agent"""
    
    def __init__(self):
        # Configure CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("🤖 Browser Agent - AI-Powered Web Automation")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Initialize components
        self.config = Config()
        self.browser_manager = None
        self.agent = None
        self.llm_processor = None
        self.task_history = []
        
        # Initialize MCP components
        self.mcp_server_manager = MCPServerManager()
        self.mcp_chat_integration = MCPChatIntegration(self.mcp_server_manager)
        
        # Create GUI elements
        self.setup_styles()
        self.create_widgets()
        self.setup_layout()
        
        # Initialize agent in background
        self.initialize_agent()
    
    def setup_styles(self):
        """Setup custom styles and themes"""
        # Define color scheme
        self.colors = {
            'primary': '#1f538d',
            'secondary': '#2d5aa0',
            'accent': '#36719f',
            'success': '#2fa572',
            'warning': '#ff8800',
            'error': '#e74c3c',
            'text': '#ffffff',
            'bg_primary': '#212121',
            'bg_secondary': '#2d2d2d',
            'bg_tertiary': '#3d3d3d'
        }
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create main container
        self.main_container = ctk.CTkFrame(self.root)
        
        # Create header
        self.create_header()
        
        # Create main content area with tabs
        self.create_tab_system()
        
        # Create status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create the header section"""
        self.header_frame = ctk.CTkFrame(self.main_container, height=80)
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.header_frame.pack_propagate(False)
        
        # Title and logo
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🤖 Browser Agent",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="AI-Powered Web Automation",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        subtitle_label.pack(side="left", padx=(10, 0))
        
        # Status indicators
        self.status_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.status_frame.pack(side="right", padx=20, pady=15)
        
        # AI Status
        self.ai_status_label = ctk.CTkLabel(
            self.status_frame,
            text="🧠 AI: Initializing...",
            font=ctk.CTkFont(size=12)
        )
        self.ai_status_label.pack(side="top", anchor="e")
        
        # Browser Status
        self.browser_status_label = ctk.CTkLabel(
            self.status_frame,
            text="🌐 Browser: Not Connected",
            font=ctk.CTkFont(size=12)
        )
        self.browser_status_label.pack(side="top", anchor="e")
        
        # MCP Status
        self.mcp_status_label = ctk.CTkLabel(
            self.status_frame,
            text="🔌 MCP: 0 servers",
            font=ctk.CTkFont(size=12)
        )
        self.mcp_status_label.pack(side="top", anchor="e")
    
    def create_tab_system(self):
        """Create the tabbed interface"""
        self.tab_view = ctk.CTkTabview(self.main_container)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Chat Tab (Main interaction)
        self.chat_tab = self.tab_view.add("💬 Chat")
        self.chat_interface = ChatInterface(self.chat_tab, self)
        
        # Brain/LLM Tab
        self.brain_tab = self.tab_view.add("🧠 Brain/LLM")
        self.brain_interface = BrainTab(self.brain_tab, self)
        
        # Browser Agent Tab
        self.browser_tab = self.tab_view.add("🌐 Browser Agent")
        self.browser_interface = EnhancedBrowserTab(self.browser_tab, self)
        
        # Desktop Automation Tab
        self.desktop_tab = self.tab_view.add("🖥️ Desktop Control")
        self.desktop_interface = DesktopAutomationTab(self.desktop_tab, self)
        
        # Task Log Tab
        self.task_log_tab = self.tab_view.add("📜 Task Log")
        self.task_log_interface = TaskLogTab(self.task_log_tab, self)
        
        # MCP Tab
        self.mcp_tab = self.tab_view.add("🔌 MCP")
        self.mcp_interface = MCPTab(self.mcp_tab, self)
        
        # Settings Tab
        self.settings_tab = self.tab_view.add("⚙️ Settings")
        self.settings_interface = SettingsTab(self.settings_tab, self)
        
        # Set default tab
        self.tab_view.set("💬 Chat")
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ctk.CTkFrame(self.main_container, height=30)
        self.status_bar.pack(fill="x", padx=10, pady=(5, 10))
        self.status_bar.pack_propagate(False)
        
        # Status text
        self.status_text = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=11)
        )
        self.status_text.pack(side="left", padx=10, pady=5)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.status_bar,
            width=200,
            height=10
        )
        self.progress_bar.pack(side="right", padx=10, pady=10)
        self.progress_bar.set(0)
    
    def setup_layout(self):
        """Setup the main layout"""
        self.main_container.pack(fill="both", expand=True)
    
    def initialize_agent(self):
        """Initialize the browser agent in background"""
        def init_worker():
            try:
                self.update_status("Initializing browser manager...")
                self.browser_manager = BrowserManager(
                    headless=False,
                    framework="selenium"
                )
                
                self.update_status("Initializing AI models...")
                self.llm_processor = MultiLLMProcessor(self.config)
                
                self.update_status("Initializing browser agent...")
                self.agent = BrowserAgent(self.config)
                
                # Connect browser manager to agent
                if self.agent and hasattr(self.agent, 'browser_manager'):
                    self.agent.browser_manager = self.browser_manager
                
                # Update UI
                self.root.after(0, self.on_agent_initialized)
                
            except Exception as e:
                self.root.after(0, lambda: self.on_initialization_error(str(e)))
        
        threading.Thread(target=init_worker, daemon=True).start()
    
    def on_agent_initialized(self):
        """Called when agent is successfully initialized"""
        self.update_status("Ready")
        self.ai_status_label.configure(text="🧠 AI: Ready")
        
        # Update brain tab with available models
        self.brain_interface.refresh_models()
        
        # Update browser tab with available browsers
        self.browser_interface.refresh_browsers()
        
        # Setup MCP chat integration callbacks
        self.mcp_chat_integration.set_callbacks(
            message_callback=self.chat_interface.add_message,
            status_callback=self.update_status
        )
        
        # Update MCP status
        self.update_mcp_status()
    
    def on_initialization_error(self, error_message: str):
        """Called when agent initialization fails"""
        self.update_status(f"Error: {error_message}")
        self.ai_status_label.configure(text="🧠 AI: Error")
        
        # Show error dialog
        self.show_error_dialog("Initialization Error", error_message)
    
    def update_status(self, message: str, progress: Optional[float] = None):
        """Update status bar"""
        self.status_text.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
    
    def show_error_dialog(self, title: str, message: str):
        """Show error dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        # Error content
        error_frame = ctk.CTkFrame(dialog)
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        error_label = ctk.CTkLabel(
            error_frame,
            text=message,
            wraplength=350,
            font=ctk.CTkFont(size=12)
        )
        error_label.pack(pady=20)
        
        ok_button = ctk.CTkButton(
            error_frame,
            text="OK",
            command=dialog.destroy
        )
        ok_button.pack(pady=10)
    
    def show_info_dialog(self, title: str, message: str):
        """Show info dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        # Info content
        info_frame = ctk.CTkFrame(dialog)
        info_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=message,
            wraplength=350,
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(pady=20)
        
        ok_button = ctk.CTkButton(
            info_frame,
            text="OK",
            command=dialog.destroy
        )
        ok_button.pack(pady=10)
    
    def add_task_to_history(self, task_data: Dict[str, Any]):
        """Add a task to the history"""
        task_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_prompt': task_data.get('user_prompt', ''),
            'ai_response': task_data.get('ai_response', ''),
            'execution_result': task_data.get('execution_result'),
            'status': task_data.get('status', 'completed')
        }
        
        self.task_history.append(task_entry)
        
        # Update task log tab
        self.task_log_interface.refresh_history()
        
        # Save to file
        self.save_task_history()
    
    def save_task_history(self):
        """Save task history to file"""
        try:
            with open("task_history.json", "w") as f:
                json.dump(self.task_history, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving task history: {e}")
    
    def load_task_history(self):
        """Load task history from file"""
        try:
            with open("task_history.json", "r") as f:
                self.task_history = json.load(f)
        except FileNotFoundError:
            self.task_history = []
        except Exception as e:
            print(f"Error loading task history: {e}")
            self.task_history = []
    
    def update_browser_status(self, status: str, browser: str = None):
        """Update browser status in header"""
        if browser:
            self.browser_status_label.configure(text=f"🌐 Browser: {browser} ({status})")
        else:
            self.browser_status_label.configure(text=f"🌐 Browser: {status}")
    
    def update_ai_status(self, status: str, model: str = None):
        """Update AI status in header"""
        if model:
            self.ai_status_label.configure(text=f"🧠 AI: {model} ({status})")
        else:
            self.ai_status_label.configure(text=f"🧠 AI: {status}")
    
    def update_mcp_status(self):
        """Update MCP status in header"""
        connected_count = len(self.mcp_server_manager.get_connected_servers())
        self.mcp_status_label.configure(text=f"🔌 MCP: {connected_count} servers")
    
    def get_mcp_server_manager(self):
        """Get MCP server manager instance"""
        return self.mcp_server_manager
    
    def get_mcp_chat_integration(self):
        """Get MCP chat integration instance"""
        return self.mcp_chat_integration
    
    def run(self):
        """Start the GUI application"""
        # Load task history
        self.load_task_history()
        
        # Configure window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start the main loop
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        # Save task history
        self.save_task_history()
        
        # Close agent if running
        if self.agent:
            try:
                self.agent.close()
            except:
                pass
        
        # Destroy window
        self.root.destroy()


def main():
    """Main entry point for GUI application"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()