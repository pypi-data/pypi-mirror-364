import tkinter as tk
import customtkinter as ctk
import threading
from typing import Dict, Any, Optional
from datetime import datetime

from ..browsers.detector import BrowserDetector


class BrowserTab:
    """Browser control and automation interface"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.browser_detector = BrowserDetector()
        self.available_browsers = {}
        self.current_browser = None
        self.automation_logs = []
        
        self.create_widgets()
        self.setup_layout()
        self.refresh_browsers()
    
    def create_widgets(self):
        """Create browser tab widgets"""
        # Main container
        self.main_container = ctk.CTkFrame(self.parent)
        
        # Browser selection section
        self.browser_section = ctk.CTkFrame(self.main_container)
        self.create_browser_selection()
        
        # Browser control section
        self.control_section = ctk.CTkFrame(self.main_container)
        self.create_browser_controls()
        
        # Live automation logs
        self.logs_section = ctk.CTkFrame(self.main_container)
        self.create_logs_section()
        
        # Manual controls
        self.manual_section = ctk.CTkFrame(self.main_container)
        self.create_manual_controls()
    
    def create_browser_selection(self):
        """Create browser selection interface"""
        # Header
        header_label = ctk.CTkLabel(
            self.browser_section,
            text="🌐 Browser Management",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Detection section
        detection_frame = ctk.CTkFrame(self.browser_section, fg_color="transparent")
        detection_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        detect_label = ctk.CTkLabel(
            detection_frame,
            text="Available Browsers:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        detect_label.pack(side="left")
        
        self.refresh_button = ctk.CTkButton(
            detection_frame,
            text="🔄 Refresh",
            command=self.refresh_browsers,
            width=100,
            height=30
        )
        self.refresh_button.pack(side="right")
        
        # Browser list
        self.browser_list_frame = ctk.CTkFrame(self.browser_section)
        self.browser_list_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Will be populated by refresh_browsers()
    
    def create_browser_controls(self):
        """Create browser control interface"""
        # Header
        control_header = ctk.CTkLabel(
            self.control_section,
            text="🎮 Browser Controls",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        control_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Current browser status
        status_frame = ctk.CTkFrame(self.control_section, fg_color="transparent")
        status_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="Current Browser:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        status_label.pack(side="left")
        
        self.current_browser_label = ctk.CTkLabel(
            status_frame,
            text="None",
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        self.current_browser_label.pack(side="left", padx=(10, 0))
        
        # Control buttons
        controls_frame = ctk.CTkFrame(self.control_section, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.launch_button = ctk.CTkButton(
            controls_frame,
            text="🚀 Launch Browser",
            command=self.launch_browser,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.launch_button.pack(side="left", padx=(0, 10))
        
        self.close_button = ctk.CTkButton(
            controls_frame,
            text="❌ Close Browser",
            command=self.close_browser,
            height=35,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            state="disabled"
        )
        self.close_button.pack(side="left", padx=(0, 10))
        
        self.screenshot_button = ctk.CTkButton(
            controls_frame,
            text="📸 Screenshot",
            command=self.take_screenshot,
            height=35,
            state="disabled"
        )
        self.screenshot_button.pack(side="left", padx=(0, 10))
        
        # Browser settings
        settings_frame = ctk.CTkFrame(self.control_section, fg_color="transparent")
        settings_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Headless mode
        self.headless_var = ctk.BooleanVar()
        self.headless_checkbox = ctk.CTkCheckBox(
            settings_frame,
            text="Headless Mode",
            variable=self.headless_var,
            font=ctk.CTkFont(size=11)
        )
        self.headless_checkbox.pack(side="left", padx=(0, 20))
        
        # Window size
        size_label = ctk.CTkLabel(
            settings_frame,
            text="Window Size:",
            font=ctk.CTkFont(size=11)
        )
        size_label.pack(side="left", padx=(0, 5))
        
        self.width_entry = ctk.CTkEntry(
            settings_frame,
            placeholder_text="1920",
            width=60
        )
        self.width_entry.pack(side="left", padx=(0, 5))
        self.width_entry.insert(0, "1920")
        
        x_label = ctk.CTkLabel(
            settings_frame,
            text="×",
            font=ctk.CTkFont(size=11)
        )
        x_label.pack(side="left")
        
        self.height_entry = ctk.CTkEntry(
            settings_frame,
            placeholder_text="1080",
            width=60
        )
        self.height_entry.pack(side="left", padx=(5, 0))
        self.height_entry.insert(0, "1080")
    
    def create_logs_section(self):
        """Create live automation logs section"""
        # Header
        logs_header = ctk.CTkLabel(
            self.logs_section,
            text="📋 Live Automation Logs",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        logs_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Logs display
        logs_frame = ctk.CTkFrame(self.logs_section)
        logs_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        self.logs_display = ctk.CTkTextbox(
            logs_frame,
            height=200,
            font=ctk.CTkFont(size=10, family="monospace")
        )
        self.logs_display.pack(fill="both", expand=True, padx=10, pady=10)
        self.logs_display.configure(state="disabled")
        
        # Log controls
        log_controls = ctk.CTkFrame(self.logs_section, fg_color="transparent")
        log_controls.pack(fill="x", padx=20, pady=(0, 20))
        
        self.clear_logs_button = ctk.CTkButton(
            log_controls,
            text="🗑️ Clear Logs",
            command=self.clear_logs,
            height=30,
            width=100
        )
        self.clear_logs_button.pack(side="left")
        
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        self.auto_scroll_checkbox = ctk.CTkCheckBox(
            log_controls,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            font=ctk.CTkFont(size=11)
        )
        self.auto_scroll_checkbox.pack(side="right")
    
    def create_manual_controls(self):
        """Create manual browser control interface"""
        # Header
        manual_header = ctk.CTkLabel(
            self.manual_section,
            text="🕹️ Manual Browser Control",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        manual_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # URL navigation
        nav_frame = ctk.CTkFrame(self.manual_section, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        nav_label = ctk.CTkLabel(
            nav_frame,
            text="Navigate to:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100
        )
        nav_label.pack(side="left")
        
        self.url_entry = ctk.CTkEntry(
            nav_frame,
            placeholder_text="https://example.com",
            font=ctk.CTkFont(size=11)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        
        self.navigate_button = ctk.CTkButton(
            nav_frame,
            text="Go",
            command=self.navigate_to_url,
            width=60,
            height=30,
            state="disabled"
        )
        self.navigate_button.pack(side="right")
        
        # Element interaction
        element_frame = ctk.CTkFrame(self.manual_section, fg_color="transparent")
        element_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        element_label = ctk.CTkLabel(
            element_frame,
            text="Element Selector:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100
        )
        element_label.pack(side="left")
        
        self.selector_entry = ctk.CTkEntry(
            element_frame,
            placeholder_text="css:button, id:submit, text:Click Me",
            font=ctk.CTkFont(size=11)
        )
        self.selector_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        
        # Element action buttons
        action_buttons = ctk.CTkFrame(self.manual_section, fg_color="transparent")
        action_buttons.pack(fill="x", padx=20, pady=(0, 20))
        
        self.click_button = ctk.CTkButton(
            action_buttons,
            text="👆 Click",
            command=lambda: self.perform_action("click"),
            width=80,
            height=30,
            state="disabled"
        )
        self.click_button.pack(side="left", padx=(0, 5))
        
        self.type_button = ctk.CTkButton(
            action_buttons,
            text="⌨️ Type",
            command=lambda: self.perform_action("type"),
            width=80,
            height=30,
            state="disabled"
        )
        self.type_button.pack(side="left", padx=(0, 5))
        
        self.scroll_button = ctk.CTkButton(
            action_buttons,
            text="📜 Scroll",
            command=lambda: self.perform_action("scroll"),
            width=80,
            height=30,
            state="disabled"
        )
        self.scroll_button.pack(side="left", padx=(0, 5))
        
        # Text input for type action
        self.type_text_entry = ctk.CTkEntry(
            action_buttons,
            placeholder_text="Text to type...",
            font=ctk.CTkFont(size=11),
            state="disabled"
        )
        self.type_text_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))
    
    def setup_layout(self):
        """Setup the layout"""
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.browser_section.pack(fill="x", pady=(0, 10))
        self.control_section.pack(fill="x", pady=(0, 10))
        self.logs_section.pack(fill="both", expand=True, pady=(0, 10))
        self.manual_section.pack(fill="x")
    
    def refresh_browsers(self):
        """Refresh available browsers list"""
        def refresh_worker():
            try:
                # Detect browsers
                browsers = self.browser_detector.detect_all()
                running_browsers = self.browser_detector.get_running_browsers()
                
                # Update UI on main thread
                self.parent.after(0, lambda: self.update_browser_list(browsers, running_browsers))
                
            except Exception as e:
                self.parent.after(0, lambda: self.add_log(f"Error detecting browsers: {e}", "error"))
        
        threading.Thread(target=refresh_worker, daemon=True).start()
    
    def update_browser_list(self, browsers, running_browsers):
        """Update browser list display"""
        self.available_browsers = browsers
        
        # Clear existing widgets
        for widget in self.browser_list_frame.winfo_children():
            widget.destroy()
        
        if not browsers:
            no_browsers_label = ctk.CTkLabel(
                self.browser_list_frame,
                text="No browsers detected. Please ensure browsers are installed.",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            no_browsers_label.pack(pady=20)
            return
        
        # Create browser cards
        for name, info in browsers.items():
            self.create_browser_card(name, info, name.lower() in running_browsers)
    
    def create_browser_card(self, name, info, is_running):
        """Create a browser information card"""
        card = ctk.CTkFrame(self.browser_list_frame)
        card.pack(fill="x", padx=10, pady=5)
        
        # Header with browser name and status
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        # Browser icon and name
        browser_icons = {
            "Chrome": "🔴",
            "Firefox": "🟠", 
            "Edge": "🔵",
            "Safari": "🟡",
            "Opera": "🟣"
        }
        
        icon = ctk.CTkLabel(
            header_frame,
            text=browser_icons.get(info.name, "🌐"),
            font=ctk.CTkFont(size=16)
        )
        icon.pack(side="left")
        
        name_label = ctk.CTkLabel(
            header_frame,
            text=info.name,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(side="left", padx=(10, 0))
        
        # Status indicator
        status_color = "#4CAF50" if info.is_installed else "#e74c3c"
        status_text = "✅ Installed" if info.is_installed else "❌ Not Found"
        
        if is_running:
            status_text += " (Running)"
            status_color = "#FF9800"
        
        status_label = ctk.CTkLabel(
            header_frame,
            text=status_text,
            font=ctk.CTkFont(size=11),
            text_color=status_color
        )
        status_label.pack(side="right")
        
        # Details
        if info.is_installed:
            details_frame = ctk.CTkFrame(card, fg_color="transparent")
            details_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            if info.version:
                version_label = ctk.CTkLabel(
                    details_frame,
                    text=f"Version: {info.version}",
                    font=ctk.CTkFont(size=10),
                    text_color="#666666"
                )
                version_label.pack(side="left")
            
            path_label = ctk.CTkLabel(
                details_frame,
                text=f"Path: {info.executable_path[:50]}..." if len(info.executable_path) > 50 else f"Path: {info.executable_path}",
                font=ctk.CTkFont(size=9),
                text_color="#666666"
            )
            path_label.pack(side="bottom", anchor="w")
        
        # Select button
        if info.is_installed:
            select_button = ctk.CTkButton(
                card,
                text="Select",
                command=lambda b=name.lower(): self.select_browser(b),
                height=30,
                width=80
            )
            select_button.pack(side="right", padx=15, pady=(0, 15))
    
    def select_browser(self, browser_name):
        """Select a browser for automation"""
        self.current_browser = browser_name
        self.current_browser_label.configure(text=browser_name.title())
        self.add_log(f"Selected browser: {browser_name.title()}")
        
        # Update main window config
        if self.main_window.config:
            self.main_window.config.default_browser = browser_name
    
    def launch_browser(self):
        """Launch the selected browser"""
        if not self.current_browser:
            self.main_window.show_error_dialog("Error", "Please select a browser first.")
            return
        
        def launch_worker():
            try:
                self.parent.after(0, lambda: self.add_log(f"Launching {self.current_browser.title()}..."))
                
                # Update configuration
                self.main_window.config.headless = self.headless_var.get()
                try:
                    width = int(self.width_entry.get())
                    height = int(self.height_entry.get())
                    self.main_window.config.window_width = width
                    self.main_window.config.window_height = height
                except:
                    pass
                
                # Launch browser through agent
                if self.main_window.agent:
                    self.main_window.agent.switch_browser(self.current_browser)
                    
                    self.parent.after(0, lambda: self.on_browser_launched())
                    self.parent.after(0, lambda: self.add_log(f"✅ {self.current_browser.title()} launched successfully"))
                else:
                    self.parent.after(0, lambda: self.add_log("❌ Agent not initialized", "error"))
                    
            except Exception as e:
                self.parent.after(0, lambda: self.add_log(f"❌ Failed to launch browser: {e}", "error"))
        
        threading.Thread(target=launch_worker, daemon=True).start()
    
    def on_browser_launched(self):
        """Called when browser is successfully launched"""
        self.close_button.configure(state="normal")
        self.screenshot_button.configure(state="normal")
        self.navigate_button.configure(state="normal")
        self.click_button.configure(state="normal")
        self.type_button.configure(state="normal")
        self.scroll_button.configure(state="normal")
        self.type_text_entry.configure(state="normal")
        
        # Update main window status
        self.main_window.update_browser_status("Connected", self.current_browser.title())
    
    def close_browser(self):
        """Close the current browser"""
        def close_worker():
            try:
                if self.main_window.agent:
                    self.main_window.agent.browser_manager.close_browser()
                    
                    self.parent.after(0, lambda: self.on_browser_closed())
                    self.parent.after(0, lambda: self.add_log(f"✅ Browser closed"))
                    
            except Exception as e:
                self.parent.after(0, lambda: self.add_log(f"❌ Error closing browser: {e}", "error"))
        
        threading.Thread(target=close_worker, daemon=True).start()
    
    def on_browser_closed(self):
        """Called when browser is closed"""
        self.close_button.configure(state="disabled")
        self.screenshot_button.configure(state="disabled")
        self.navigate_button.configure(state="disabled")
        self.click_button.configure(state="disabled")
        self.type_button.configure(state="disabled")
        self.scroll_button.configure(state="disabled")
        self.type_text_entry.configure(state="disabled")
        
        # Update main window status
        self.main_window.update_browser_status("Disconnected")
    
    def take_screenshot(self):
        """Take a screenshot of the current page"""
        def screenshot_worker():
            try:
                if self.main_window.agent and self.main_window.agent.automation:
                    import asyncio
                    screenshot_path = asyncio.run(self.main_window.agent.automation.take_screenshot())
                    
                    if screenshot_path:
                        self.parent.after(0, lambda: self.add_log(f"📸 Screenshot saved: {screenshot_path}"))
                    else:
                        self.parent.after(0, lambda: self.add_log("❌ Failed to take screenshot", "error"))
                        
            except Exception as e:
                self.parent.after(0, lambda: self.add_log(f"❌ Screenshot error: {e}", "error"))
        
        threading.Thread(target=screenshot_worker, daemon=True).start()
    
    def navigate_to_url(self):
        """Navigate to the specified URL"""
        url = self.url_entry.get().strip()
        if not url:
            return
        
        def navigate_worker():
            try:
                if self.main_window.agent and self.main_window.agent.automation:
                    import asyncio
                    result = asyncio.run(self.main_window.agent.automation.navigate(url))
                    
                    if result.get('success'):
                        self.parent.after(0, lambda: self.add_log(f"🌐 Navigated to: {result.get('url', url)}"))
                    else:
                        self.parent.after(0, lambda: self.add_log(f"❌ Navigation failed: {result.get('error', 'Unknown error')}", "error"))
                        
            except Exception as e:
                self.parent.after(0, lambda: self.add_log(f"❌ Navigation error: {e}", "error"))
        
        threading.Thread(target=navigate_worker, daemon=True).start()
    
    def perform_action(self, action):
        """Perform a manual browser action"""
        selector = self.selector_entry.get().strip()
        if not selector:
            self.add_log("❌ Please enter an element selector", "error")
            return
        
        def action_worker():
            try:
                if self.main_window.agent and self.main_window.agent.automation:
                    import asyncio
                    
                    if action == "click":
                        result = asyncio.run(self.main_window.agent.automation.click_element(selector))
                    elif action == "type":
                        text = self.type_text_entry.get().strip()
                        if not text:
                            self.parent.after(0, lambda: self.add_log("❌ Please enter text to type", "error"))
                            return
                        result = asyncio.run(self.main_window.agent.automation.type_text(selector, text))
                    elif action == "scroll":
                        result = asyncio.run(self.main_window.agent.automation.scroll(selector))
                    else:
                        result = {'success': False, 'error': 'Unknown action'}
                    
                    if result.get('success'):
                        self.parent.after(0, lambda: self.add_log(f"✅ {action.title()} action successful"))
                    else:
                        self.parent.after(0, lambda: self.add_log(f"❌ {action.title()} failed: {result.get('error', 'Unknown error')}", "error"))
                        
            except Exception as e:
                self.parent.after(0, lambda: self.add_log(f"❌ {action.title()} error: {e}", "error"))
        
        threading.Thread(target=action_worker, daemon=True).start()
    
    def add_log(self, message, level="info"):
        """Add a log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding
        colors = {
            "info": "#FFFFFF",
            "error": "#e74c3c",
            "warning": "#f39c12",
            "success": "#2ecc71"
        }
        
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.logs_display.configure(state="normal")
        self.logs_display.insert("end", formatted_message)
        
        if self.auto_scroll_var.get():
            self.logs_display.see("end")
        
        self.logs_display.configure(state="disabled")
        
        # Store log
        self.automation_logs.append({
            'timestamp': timestamp,
            'message': message,
            'level': level
        })
    
    def clear_logs(self):
        """Clear the logs display"""
        self.logs_display.configure(state="normal")
        self.logs_display.delete("1.0", "end")
        self.logs_display.configure(state="disabled")
        self.automation_logs.clear()