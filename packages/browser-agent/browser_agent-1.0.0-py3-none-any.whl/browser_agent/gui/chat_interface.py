import tkinter as tk
import customtkinter as ctk
import asyncio
import threading
from typing import Dict, Any, Optional
from datetime import datetime
import time
from .placeholder_utils import PlaceholderTextbox


class ModernChatBubble(ctk.CTkFrame):
    """Modern chat bubble widget with professional styling"""
    
    def __init__(self, parent, message: str, sender: str, timestamp: str, **kwargs):
        # Configure bubble colors based on sender
        if sender == "user":
            fg_color = ("#007AFF", "#0056CC")  # Blue gradient
            text_color = "white"
            corner_radius = 20
        elif sender == "ai":
            fg_color = ("#F2F2F7", "#1C1C1E")  # Light/dark adaptive
            text_color = ("#000000", "#FFFFFF")
            corner_radius = 20
        else:  # system
            fg_color = ("#FF9500", "#FF8C00")  # Orange
            text_color = "white"
            corner_radius = 15
            
        super().__init__(parent, fg_color=fg_color, corner_radius=corner_radius, **kwargs)
        
        self.sender = sender
        self.create_bubble_content(message, sender, timestamp, text_color)
    
    def create_bubble_content(self, message: str, sender: str, timestamp: str, text_color: str):
        """Create the content inside the chat bubble"""
        # Sender icon and name
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        # Icon and sender name
        if sender == "user":
            icon = "👤"
            name = "You"
        elif sender == "ai":
            icon = "🤖"
            name = "Assistant"
        else:
            icon = "⚙️"
            name = "System"
            
        sender_label = ctk.CTkLabel(
            header_frame,
            text=f"{icon} {name}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=text_color
        )
        sender_label.pack(side="left")
        
        # Timestamp
        time_label = ctk.CTkLabel(
            header_frame,
            text=timestamp,
            font=ctk.CTkFont(size=10),
            text_color=(text_color if sender == "user" else "#8E8E93")
        )
        time_label.pack(side="right")
        
        # Message content
        message_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=13, family="SF Pro Display"),
            text_color=text_color,
            wraplength=500,
            justify="left",
            anchor="w"
        )
        message_label.pack(fill="x", padx=15, pady=(0, 15))


class AnimatedTextWidget(ctk.CTkScrollableFrame):
    """Modern scrollable chat container with bubble messages"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(fg_color=("#FFFFFF", "#000000"))  # Clean background
        
    def add_message(self, message: str, sender: str = "user", animate: bool = False):
        """Add a message bubble to the chat"""
        timestamp = datetime.now().strftime("%H:%M")
        
        # Create container for proper alignment
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=10, pady=5)
        
        # Create the chat bubble
        bubble = ModernChatBubble(container, message, sender, timestamp)
        
        # Align bubble based on sender
        if sender == "user":
            bubble.pack(side="right", anchor="e", padx=(50, 0))
        else:
            bubble.pack(side="left", anchor="w", padx=(0, 50))
        
        # Auto-scroll to bottom
        self.after(100, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        """Scroll to the bottom of the chat"""
        self._parent_canvas.yview_moveto(1.0)
    
    def clear_messages(self):
        """Clear all messages from chat"""
        for widget in self.winfo_children():
            widget.destroy()


class ChatInterface:
    """Modern, professional chat interface for interacting with the AI agent"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.is_processing = False
        
        # Modern color scheme
        self.colors = {
            'primary': '#007AFF',
            'secondary': '#5856D6', 
            'success': '#34C759',
            'warning': '#FF9500',
            'error': '#FF3B30',
            'background': ('#F2F2F7', '#000000'),
            'surface': ('#FFFFFF', '#1C1C1E'),
            'text_primary': ('#000000', '#FFFFFF'),
            'text_secondary': '#8E8E93'
        }
        
        self.create_widgets()
        self.setup_layout()
        
        # Welcome message
        self.add_welcome_message()
    
    def create_widgets(self):
        """Create modern chat interface widgets with professional styling"""
        # Main chat container with gradient-like effect
        self.chat_container = ctk.CTkFrame(
            self.parent, 
            fg_color=self.colors['background'],
            corner_radius=0
        )
        
        # Header section
        self.create_chat_header()
        
        # Chat display area with modern styling
        self.chat_frame = ctk.CTkFrame(
            self.chat_container,
            fg_color=self.colors['surface'],
            corner_radius=15
        )
        
        # Modern chat display with bubble messages
        self.chat_display = AnimatedTextWidget(
            self.chat_frame,
            height=450,
            corner_radius=10
        )
        
        # Modern input section
        self.create_input_section()
        
        # Enhanced quick actions
        self.create_modern_quick_actions()
        
        # Status and typing indicators
        self.create_status_section()
    
    def create_chat_header(self):
        """Create a modern chat header"""
        self.header_frame = ctk.CTkFrame(
            self.chat_container,
            fg_color=self.colors['primary'],
            corner_radius=15,
            height=60
        )
        self.header_frame.pack_propagate(False)
        
        # Title and status
        title_label = ctk.CTkLabel(
            self.header_frame,
            text="💬 AI Assistant Chat",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # Online status indicator
        self.status_indicator = ctk.CTkLabel(
            self.header_frame,
            text="🟢 Online",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        self.status_indicator.pack(side="right", padx=20, pady=15)
    
    def create_input_section(self):
        """Create modern input section with enhanced styling"""
        # Input container with elevated appearance
        self.input_container = ctk.CTkFrame(
            self.chat_container,
            fg_color=self.colors['surface'],
            corner_radius=15
        )
        
        # Input text area with modern styling
        self.input_text = PlaceholderTextbox(
            self.input_container,
            height=60,
            font=ctk.CTkFont(size=14, family="SF Pro Display"),
            placeholder_text="✨ Ask me anything... I can help with web automation, desktop tasks, and more!",
            corner_radius=10,
            border_width=2,
            border_color=self.colors['primary']
        )
        
        # Action buttons with modern design
        self.create_action_buttons()
    
    def create_action_buttons(self):
        """Create modern action buttons"""
        self.button_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        
        # Send button with primary styling
        self.send_button = ctk.CTkButton(
            self.button_frame,
            text="Send ✈️",
            command=self.send_message,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=100,
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            corner_radius=22
        )
        
        # MCP button with secondary styling
        self.mcp_button = ctk.CTkButton(
            self.button_frame,
            text="🔌 MCP",
            command=self.open_mcp_menu,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            width=80,
            fg_color=self.colors['secondary'],
            hover_color="#4C4CDB",
            corner_radius=20
        )
        
        # Clear button with subtle styling
        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="🗑️",
            command=self.clear_chat,
            font=ctk.CTkFont(size=12),
            height=40,
            width=50,
            fg_color="transparent",
            hover_color=("#E5E5EA", "#2C2C2E"),
            border_width=1,
            border_color=self.colors['text_secondary'],
            corner_radius=20
        )
        
        # Stop button (hidden by default)
        self.stop_button = ctk.CTkButton(
            self.button_frame,
            text="⏹️ Stop",
            command=self.stop_processing,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            width=80,
            fg_color=self.colors['error'],
            hover_color="#D70015",
            corner_radius=20
        )
    
    def create_status_section(self):
        """Create modern status and typing indicators"""
        self.status_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        
        # Status label with modern styling
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="💡 Ready to assist you",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        
        # Modern typing indicator
        self.typing_indicator = ctk.CTkLabel(
            self.status_frame,
            text="🤖 AI is thinking",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['success']
        )
    
    def create_modern_quick_actions(self):
        """Create modern quick action buttons with categories"""
        self.quick_actions_frame = ctk.CTkFrame(
            self.chat_container,
            fg_color=self.colors['surface'],
            corner_radius=15
        )
        
        # Header for quick actions
        header_frame = ctk.CTkFrame(self.quick_actions_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        quick_actions_label = ctk.CTkLabel(
            header_frame,
            text="⚡ Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        quick_actions_label.pack(side="left")
        
        # Toggle button for quick actions
        self.toggle_actions_btn = ctk.CTkButton(
            header_frame,
            text="▼",
            command=self.toggle_quick_actions,
            width=30,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=("#E5E5EA", "#2C2C2E")
        )
        self.toggle_actions_btn.pack(side="right")
        
        # Actions container
        self.actions_container = ctk.CTkFrame(self.quick_actions_frame, fg_color="transparent")
        self.actions_container.pack(fill="x", padx=15, pady=(0, 15))
        
        # Categorized quick actions
        self.create_action_categories()
    
    def create_action_categories(self):
        """Create categorized action buttons"""
        categories = {
            "🌐 Web Tasks": [
                ("🔍 Search Google", "Search Google for 'latest AI news'"),
                ("📧 Gmail", "Go to Gmail and check for new emails"),
                ("🛒 Amazon", "Go to Amazon and search for 'wireless headphones'")
            ],
            "🖥️ Desktop Tasks": [
                ("🧮 Calculator", "Open Calculator app and calculate 15% tip on $45"),
                ("📸 Screenshot", "Take a screenshot of the current screen"),
                ("📝 TextEdit", "Open TextEdit and type a quick note")
            ],
            "📊 Information": [
                ("🌡️ Weather", "Check the weather forecast for today"),
                ("💰 Stocks", "Check the current stock price of Apple"),
                ("🖱️ Mouse Position", "Get the current mouse position coordinates")
            ]
        }
        
        for category, actions in categories.items():
            # Category header
            cat_frame = ctk.CTkFrame(self.actions_container, fg_color="transparent")
            cat_frame.pack(fill="x", pady=(10, 5))
            
            cat_label = ctk.CTkLabel(
                cat_frame,
                text=category,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors['text_secondary']
            )
            cat_label.pack(anchor="w")
            
            # Action buttons in a row
            btn_frame = ctk.CTkFrame(self.actions_container, fg_color="transparent")
            btn_frame.pack(fill="x", pady=(0, 5))
            
            for action_text, action_prompt in actions:
                btn = ctk.CTkButton(
                    btn_frame,
                    text=action_text,
                    command=lambda p=action_prompt: self.send_quick_action(p),
                    font=ctk.CTkFont(size=11),
                    height=35,
                    width=140,
                    fg_color="transparent",
                    hover_color=("#E5E5EA", "#2C2C2E"),
                    border_width=1,
                    border_color=self.colors['text_secondary'],
                    corner_radius=17
                )
                btn.pack(side="left", padx=(0, 8))
    
    def toggle_quick_actions(self):
        """Toggle quick actions visibility"""
        if self.actions_container.winfo_viewable():
            self.actions_container.pack_forget()
            self.toggle_actions_btn.configure(text="▶")
        else:
            self.actions_container.pack(fill="x", padx=15, pady=(0, 15))
            self.toggle_actions_btn.configure(text="▼")
    
    def setup_layout(self):
        """Setup the modern layout of chat interface"""
        self.chat_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        self.header_frame.pack(fill="x", pady=(0, 15))
        
        # Chat display area with modern spacing
        self.chat_frame.pack(fill="both", expand=True, pady=(0, 15))
        self.chat_display.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Quick actions (collapsible)
        self.quick_actions_frame.pack(fill="x", pady=(0, 15))
        
        # Input section with modern layout
        self.input_container.pack(fill="x")
        self.input_text.pack(fill="x", padx=15, pady=(15, 10))
        
        # Status section
        self.status_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.status_label.pack(side="left")
        
        # Button section with proper spacing
        self.button_frame.pack(fill="x", padx=15, pady=(0, 15))
        self.send_button.pack(side="right", padx=(8, 0))
        self.clear_button.pack(side="right", padx=(8, 0))
        self.mcp_button.pack(side="right", padx=(8, 0))
        
        # Hide typing indicator and stop button initially
        self.hide_typing_indicator()
        self.hide_stop_button()
        
        # Enhanced keyboard shortcuts
        self.input_text.bind("<Return>", lambda e: self.send_message() if not e.state & 0x1 else None)
        self.input_text.bind("<Control-Return>", lambda e: self.send_message())
        self.input_text.bind("<Shift-Return>", lambda e: None)  # Allow line breaks
    

    
    def add_welcome_message(self):
        """Add modern welcome message to chat"""
        welcome_text = """Hello! I'm your AI-powered automation assistant. 👋

I can help you with web browsing, desktop automation, and complex multi-step tasks. Here's what I can do:

🌐 Web Automation
• Browse websites and search for information
• Fill forms and submit data automatically
• Extract content and compare prices
• Manage emails and social media

🖥️ Desktop Control
• Open applications and manage windows
• Take screenshots and control mouse/keyboard
• Automate repetitive desktop tasks
• Coordinate between different apps

🔌 Advanced Integration
• Connect to external tools via MCP
• Access filesystems and databases
• Use specialized automation servers

Just describe what you need in plain English, and I'll handle the technical details!

Try something like:
• "Search for the latest iPhone on Apple's website"
• "Take a screenshot and open Calculator"
• "Check my Gmail for important emails"

What can I help you with today?"""
        
        self.chat_display.add_message(welcome_text, "ai", animate=True)
    
    def send_message(self):
        """Send user message and process with AI"""
        if self.is_processing:
            return
        
        user_input = self.input_text.get_actual_text().strip()
        if not user_input:
            return
        
        # Add user message to chat
        self.chat_display.add_message(user_input, "user")
        
        # Clear input
        self.input_text.set_text("")
        
        # Process message
        self.process_user_message(user_input)
    
    def send_quick_action(self, prompt: str):
        """Send a quick action prompt"""
        if self.is_processing:
            return
        
        # Set text in input area
        self.input_text.set_text(prompt)
        
        # Send the message
        self.send_message()
    
    def open_mcp_menu(self):
        """Open MCP menu for server management"""
        if hasattr(self.main_window, 'mcp_chat_integration'):
            self.main_window.mcp_chat_integration.show_mcp_menu()
        else:
            self.chat_display.add_message(
                "MCP integration is not available. Please check your configuration.",
                "system"
            )
    
    def process_user_message(self, message: str):
        """Process user message with AI agent"""
        def process_worker():
            try:
                self.set_processing_state(True)
                
                # Check if this is an MCP command first
                if hasattr(self.main_window, 'mcp_chat_integration'):
                    mcp_handled = self.main_window.mcp_chat_integration.process_mcp_message(message)
                    if mcp_handled:
                        # MCP handled the message, update status and return
                        self.root_after(0, lambda: self.main_window.update_mcp_status())
                        return
                
                # Check if this is a task execution request or just conversation
                if self.is_task_request(message):
                    # Execute as browser automation task
                    self.root_after(0, lambda: self.chat_display.add_message(
                        "I'll help you with that task. Let me analyze what needs to be done...", "ai", True
                    ))
                    
                    # Execute the task
                    result = asyncio.run(self.execute_browser_task(message))
                    
                    if result:
                        if result.success:
                            response = f"✅ Task completed successfully!\n\n"
                            response += f"⏱️ Execution time: {result.execution_time:.2f} seconds\n"
                            response += f"📝 Steps executed: {len(result.step_results)}\n"
                            
                            if result.screenshots:
                                response += f"📸 Screenshots saved: {len(result.screenshots)}\n"
                                for screenshot in result.screenshots:
                                    response += f"   • {screenshot}\n"
                        else:
                            response = f"❌ Task failed: {result.error_message}\n\n"
                            response += "Let me know if you'd like me to try a different approach!"
                    else:
                        response = "I encountered an issue while processing your request. Please check that the browser agent is properly configured."
                else:
                    # Generate conversational response
                    response = asyncio.run(self.generate_ai_response(message))
                
                # Add AI response to chat
                self.root_after(0, lambda: self.chat_display.add_message(response, "ai", True))
                
                # Add to task history
                task_data = {
                    'user_prompt': message,
                    'ai_response': response,
                    'execution_result': result if 'result' in locals() else None,
                    'status': 'completed'
                }
                self.root_after(0, lambda: self.main_window.add_task_to_history(task_data))
                
            except Exception as e:
                error_response = f"I apologize, but I encountered an error: {str(e)}\n\nPlease try again or check your configuration."
                self.root_after(0, lambda: self.chat_display.add_message(error_response, "ai"))
            finally:
                self.root_after(0, lambda: self.set_processing_state(False))
        
        threading.Thread(target=process_worker, daemon=True).start()
    
    def is_task_request(self, message: str) -> bool:
        """Determine if message is a task execution request"""
        # Check if it's an MCP command first
        if hasattr(self.main_window, 'mcp_chat_integration'):
            if self.main_window.mcp_chat_integration.is_mcp_command(message):
                return False  # MCP commands are handled separately
        
        task_keywords = [
            # Browser automation keywords
            'go to', 'navigate', 'search', 'click', 'fill', 'submit', 'download',
            'book', 'buy', 'purchase', 'find', 'extract', 'scrape', 'automate',
            'open', 'close', 'scroll', 'select', 'type', 'enter', 'compare',
            # Desktop automation keywords
            'screenshot', 'take screenshot', 'mouse position', 'move mouse',
            'press key', 'open app', 'open application', 'calculator', 'textedit',
            'finder', 'terminal', 'safari', 'click at', 'coordinates', 'drag',
            'drop', 'copy', 'paste', 'keyboard', 'desktop', 'screen'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in task_keywords)
    
    async def execute_browser_task(self, prompt: str):
        """Execute browser automation task"""
        try:
            if self.main_window.agent:
                return await self.main_window.agent.execute_task(prompt)
            else:
                raise Exception("Browser agent not initialized")
        except Exception as e:
            print(f"Error executing task: {e}")
            return None
    
    async def generate_ai_response(self, message: str) -> str:
        """Generate conversational AI response"""
        try:
            if self.main_window.llm_processor:
                return await self.main_window.llm_processor.generate_response(message)
            else:
                return "I'm still initializing my AI capabilities. Please wait a moment and try again."
        except Exception as e:
            return f"I encountered an error while processing your message: {str(e)}"
    
    def set_processing_state(self, processing: bool):
        """Set the processing state and update UI"""
        self.is_processing = processing
        
        if processing:
            self.show_typing_indicator()
            self.show_stop_button()
            self.send_button.configure(state="disabled")
            self.main_window.update_status("Processing request...", 0.5)
        else:
            self.hide_typing_indicator()
            self.hide_stop_button()
            self.send_button.configure(state="normal")
            self.main_window.update_status("Ready", 0)
    
    def show_typing_indicator(self):
        """Show typing indicator"""
        self.status_label.pack_forget()
        self.typing_indicator.pack(side="left")
        
        # Animate typing indicator
        self.animate_typing_indicator()
    
    def hide_typing_indicator(self):
        """Hide typing indicator"""
        self.typing_indicator.pack_forget()
        self.status_label.pack(side="left")
    
    def show_stop_button(self):
        """Show stop button"""
        self.stop_button.pack(side="right", padx=(5, 5))
    
    def hide_stop_button(self):
        """Hide stop button"""
        self.stop_button.pack_forget()
    
    def animate_typing_indicator(self):
        """Animate the typing indicator dots"""
        if self.is_processing:
            current_text = self.typing_indicator.cget("text")
            if current_text.endswith("..."):
                self.typing_indicator.configure(text="🤖 AI is thinking")
            else:
                self.typing_indicator.configure(text=current_text + ".")
            
            # Schedule next animation
            self.parent.after(500, self.animate_typing_indicator)
    
    def stop_processing(self):
        """Stop current processing"""
        self.set_processing_state(False)
        self.chat_display.add_message("Processing stopped by user.", "system")
    
    def clear_chat(self):
        """Clear the chat display with modern animation"""
        self.chat_display.clear_messages()
        
        # Add welcome message back
        self.add_welcome_message()
    
    def root_after(self, delay, callback):
        """Safe way to schedule GUI updates from background thread"""
        try:
            self.parent.after(delay, callback)
        except:
            pass