import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any
import json
import os


class SettingsTab:
    """Settings and configuration management interface"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.settings_changed = False
        
        self.create_widgets()
        self.setup_layout()
        self.load_settings()
    
    def create_widgets(self):
        """Create settings tab widgets"""
        # Main container
        self.main_container = ctk.CTkScrollableFrame(self.parent)
        
        # Header
        self.header_section = ctk.CTkFrame(self.main_container)
        self.create_header()
        
        # General settings
        self.general_section = ctk.CTkFrame(self.main_container)
        self.create_general_settings()
        
        # Browser settings
        self.browser_section = ctk.CTkFrame(self.main_container)
        self.create_browser_settings()
        
        # Automation settings
        self.automation_section = ctk.CTkFrame(self.main_container)
        self.create_automation_settings()
        
        # Security settings
        self.security_section = ctk.CTkFrame(self.main_container)
        self.create_security_settings()
        
        # Performance settings
        self.performance_section = ctk.CTkFrame(self.main_container)
        self.create_performance_settings()
        
        # Advanced settings
        self.advanced_section = ctk.CTkFrame(self.main_container)
        self.create_advanced_settings()
        
        # Actions
        self.actions_section = ctk.CTkFrame(self.main_container)
        self.create_actions()
    
    def create_header(self):
        """Create header section"""
        title_label = ctk.CTkLabel(
            self.header_section,
            text="⚙️ Settings & Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        subtitle_label = ctk.CTkLabel(
            self.header_section,
            text="Configure Browser Agent behavior and preferences",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        subtitle_label.pack(anchor="w", padx=20, pady=(0, 20))
    
    def create_general_settings(self):
        """Create general settings section"""
        self.create_section_header(self.general_section, "🔧 General Settings")
        
        # Default browser
        browser_frame = self.create_setting_frame(self.general_section)
        self.create_setting_label(browser_frame, "Default Browser:")
        self.default_browser_menu = ctk.CTkOptionMenu(
            browser_frame,
            values=["chrome", "firefox", "edge", "safari"],
            width=150
        )
        self.default_browser_menu.pack(side="left", padx=(10, 0))
        
        # Theme
        theme_frame = self.create_setting_frame(self.general_section)
        self.create_setting_label(theme_frame, "Theme:")
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            width=150,
            command=self.on_theme_change
        )
        self.theme_menu.pack(side="left", padx=(10, 0))
        
        # Log level
        log_frame = self.create_setting_frame(self.general_section)
        self.create_setting_label(log_frame, "Log Level:")
        self.log_level_menu = ctk.CTkOptionMenu(
            log_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            width=150
        )
        self.log_level_menu.pack(side="left", padx=(10, 0))
        
        # Auto-save settings
        autosave_frame = self.create_setting_frame(self.general_section)
        self.autosave_var = ctk.BooleanVar(value=True)
        self.autosave_checkbox = ctk.CTkCheckBox(
            autosave_frame,
            text="Auto-save settings on change",
            variable=self.autosave_var
        )
        self.autosave_checkbox.pack(side="left")
    
    def create_browser_settings(self):
        """Create browser settings section"""
        self.create_section_header(self.browser_section, "🌐 Browser Settings")
        
        # Automation framework
        framework_frame = self.create_setting_frame(self.browser_section)
        self.create_setting_label(framework_frame, "Automation Framework:")
        self.framework_menu = ctk.CTkOptionMenu(
            framework_frame,
            values=["selenium", "playwright"],
            width=150
        )
        self.framework_menu.pack(side="left", padx=(10, 0))
        
        # Window size
        size_frame = self.create_setting_frame(self.browser_section)
        self.create_setting_label(size_frame, "Default Window Size:")
        
        self.width_entry = ctk.CTkEntry(
            size_frame,
            placeholder_text="1920",
            width=80
        )
        self.width_entry.pack(side="left", padx=(10, 5))
        
        x_label = ctk.CTkLabel(size_frame, text="×", font=ctk.CTkFont(size=11))
        x_label.pack(side="left")
        
        self.height_entry = ctk.CTkEntry(
            size_frame,
            placeholder_text="1080",
            width=80
        )
        self.height_entry.pack(side="left", padx=(5, 0))
        
        # Browser options
        options_frame = self.create_setting_frame(self.browser_section)
        
        self.headless_var = ctk.BooleanVar()
        self.headless_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Headless mode by default",
            variable=self.headless_var
        )
        self.headless_checkbox.pack(side="left", padx=(0, 20))
        
        self.incognito_var = ctk.BooleanVar()
        self.incognito_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Use incognito/private mode",
            variable=self.incognito_var
        )
        self.incognito_checkbox.pack(side="left")
        
        # Timeouts
        timeout_frame = self.create_setting_frame(self.browser_section)
        self.create_setting_label(timeout_frame, "Page Load Timeout (s):")
        self.page_timeout_entry = ctk.CTkEntry(
            timeout_frame,
            placeholder_text="30",
            width=80
        )
        self.page_timeout_entry.pack(side="left", padx=(10, 20))
        
        self.create_setting_label(timeout_frame, "Implicit Wait (s):")
        self.implicit_wait_entry = ctk.CTkEntry(
            timeout_frame,
            placeholder_text="10",
            width=80
        )
        self.implicit_wait_entry.pack(side="left", padx=(10, 0))
    
    def create_automation_settings(self):
        """Create automation settings section"""
        self.create_section_header(self.automation_section, "🤖 Automation Settings")
        
        # Human-like behavior
        behavior_frame = self.create_setting_frame(self.automation_section)
        
        self.human_delays_var = ctk.BooleanVar(value=True)
        self.human_delays_checkbox = ctk.CTkCheckBox(
            behavior_frame,
            text="Human-like delays",
            variable=self.human_delays_var
        )
        self.human_delays_checkbox.pack(side="left", padx=(0, 20))
        
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        self.auto_scroll_checkbox = ctk.CTkCheckBox(
            behavior_frame,
            text="Auto-scroll to elements",
            variable=self.auto_scroll_var
        )
        self.auto_scroll_checkbox.pack(side="left")
        
        # Delay settings
        delay_frame = self.create_setting_frame(self.automation_section)
        self.create_setting_label(delay_frame, "Min Delay (s):")
        self.min_delay_entry = ctk.CTkEntry(
            delay_frame,
            placeholder_text="0.5",
            width=80
        )
        self.min_delay_entry.pack(side="left", padx=(10, 20))
        
        self.create_setting_label(delay_frame, "Max Delay (s):")
        self.max_delay_entry = ctk.CTkEntry(
            delay_frame,
            placeholder_text="2.0",
            width=80
        )
        self.max_delay_entry.pack(side="left", padx=(10, 0))
        
        # Screenshot settings
        screenshot_frame = self.create_setting_frame(self.automation_section)
        
        self.screenshot_error_var = ctk.BooleanVar(value=True)
        self.screenshot_error_checkbox = ctk.CTkCheckBox(
            screenshot_frame,
            text="Screenshot on error",
            variable=self.screenshot_error_var
        )
        self.screenshot_error_checkbox.pack(side="left", padx=(0, 20))
        
        self.screenshot_success_var = ctk.BooleanVar()
        self.screenshot_success_checkbox = ctk.CTkCheckBox(
            screenshot_frame,
            text="Screenshot on success",
            variable=self.screenshot_success_var
        )
        self.screenshot_success_checkbox.pack(side="left")
    
    def create_security_settings(self):
        """Create security settings section"""
        self.create_section_header(self.security_section, "🔒 Security Settings")
        
        # Permissions
        permissions_frame = self.create_setting_frame(self.security_section)
        
        self.allow_downloads_var = ctk.BooleanVar()
        self.allow_downloads_checkbox = ctk.CTkCheckBox(
            permissions_frame,
            text="Allow file downloads",
            variable=self.allow_downloads_var
        )
        self.allow_downloads_checkbox.pack(anchor="w", pady=2)
        
        self.allow_notifications_var = ctk.BooleanVar()
        self.allow_notifications_checkbox = ctk.CTkCheckBox(
            permissions_frame,
            text="Allow notifications",
            variable=self.allow_notifications_var
        )
        self.allow_notifications_checkbox.pack(anchor="w", pady=2)
        
        self.allow_location_var = ctk.BooleanVar()
        self.allow_location_checkbox = ctk.CTkCheckBox(
            permissions_frame,
            text="Allow location access",
            variable=self.allow_location_var
        )
        self.allow_location_checkbox.pack(anchor="w", pady=2)
        
        self.allow_camera_var = ctk.BooleanVar()
        self.allow_camera_checkbox = ctk.CTkCheckBox(
            permissions_frame,
            text="Allow camera access",
            variable=self.allow_camera_var
        )
        self.allow_camera_checkbox.pack(anchor="w", pady=2)
        
        self.allow_microphone_var = ctk.BooleanVar()
        self.allow_microphone_checkbox = ctk.CTkCheckBox(
            permissions_frame,
            text="Allow microphone access",
            variable=self.allow_microphone_var
        )
        self.allow_microphone_checkbox.pack(anchor="w", pady=2)
        
        # Container settings
        container_frame = self.create_setting_frame(self.security_section)
        
        self.use_container_var = ctk.BooleanVar()
        self.use_container_checkbox = ctk.CTkCheckBox(
            container_frame,
            text="Use Docker container for isolation",
            variable=self.use_container_var
        )
        self.use_container_checkbox.pack(side="left")
    
    def create_performance_settings(self):
        """Create performance settings section"""
        self.create_section_header(self.performance_section, "⚡ Performance Settings")
        
        # Plugins
        plugins_frame = self.create_setting_frame(self.performance_section)
        
        self.plugins_enabled_var = ctk.BooleanVar(value=True)
        self.plugins_enabled_checkbox = ctk.CTkCheckBox(
            plugins_frame,
            text="Enable plugins system",
            variable=self.plugins_enabled_var
        )
        self.plugins_enabled_checkbox.pack(side="left")
        
        # Memory management
        memory_frame = self.create_setting_frame(self.performance_section)
        self.create_setting_label(memory_frame, "Max Memory Usage (MB):")
        self.max_memory_entry = ctk.CTkEntry(
            memory_frame,
            placeholder_text="2048",
            width=100
        )
        self.max_memory_entry.pack(side="left", padx=(10, 0))
        
        # Concurrent tasks
        concurrent_frame = self.create_setting_frame(self.performance_section)
        self.create_setting_label(concurrent_frame, "Max Concurrent Tasks:")
        self.max_concurrent_entry = ctk.CTkEntry(
            concurrent_frame,
            placeholder_text="3",
            width=80
        )
        self.max_concurrent_entry.pack(side="left", padx=(10, 0))
    
    def create_advanced_settings(self):
        """Create advanced settings section"""
        self.create_section_header(self.advanced_section, "🔬 Advanced Settings")
        
        # User agent
        ua_frame = self.create_setting_frame(self.advanced_section)
        self.create_setting_label(ua_frame, "Custom User Agent:")
        self.user_agent_entry = ctk.CTkEntry(
            ua_frame,
            placeholder_text="Leave empty for default",
            width=400
        )
        self.user_agent_entry.pack(side="left", padx=(10, 0))
        
        # Proxy settings
        proxy_frame = self.create_setting_frame(self.advanced_section)
        self.create_setting_label(proxy_frame, "Proxy Server:")
        self.proxy_entry = ctk.CTkEntry(
            proxy_frame,
            placeholder_text="http://proxy:port",
            width=200
        )
        self.proxy_entry.pack(side="left", padx=(10, 0))
        
        # Debug mode
        debug_frame = self.create_setting_frame(self.advanced_section)
        
        self.debug_mode_var = ctk.BooleanVar()
        self.debug_mode_checkbox = ctk.CTkCheckBox(
            debug_frame,
            text="Debug mode (detailed logging)",
            variable=self.debug_mode_var
        )
        self.debug_mode_checkbox.pack(side="left", padx=(0, 20))
        
        self.dev_tools_var = ctk.BooleanVar()
        self.dev_tools_checkbox = ctk.CTkCheckBox(
            debug_frame,
            text="Open browser dev tools",
            variable=self.dev_tools_var
        )
        self.dev_tools_checkbox.pack(side="left")
        
        # Configuration file path
        config_frame = self.create_setting_frame(self.advanced_section)
        self.create_setting_label(config_frame, "Config File:")
        self.config_path_entry = ctk.CTkEntry(
            config_frame,
            placeholder_text="config.json",
            width=250
        )
        self.config_path_entry.pack(side="left", padx=(10, 5))
        
        self.browse_config_button = ctk.CTkButton(
            config_frame,
            text="Browse",
            command=self.browse_config_file,
            width=80,
            height=25
        )
        self.browse_config_button.pack(side="left")
    
    def create_actions(self):
        """Create action buttons section"""
        self.create_section_header(self.actions_section, "💾 Actions")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.actions_section, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Save button
        self.save_button = ctk.CTkButton(
            buttons_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.save_button.pack(side="left", padx=(0, 10))
        
        # Reset button
        self.reset_button = ctk.CTkButton(
            buttons_frame,
            text="🔄 Reset to Defaults",
            command=self.reset_to_defaults,
            height=35,
            fg_color="#666666",
            hover_color="#777777"
        )
        self.reset_button.pack(side="left", padx=(0, 10))
        
        # Export button
        self.export_button = ctk.CTkButton(
            buttons_frame,
            text="📁 Export Config",
            command=self.export_config,
            height=35
        )
        self.export_button.pack(side="left", padx=(0, 10))
        
        # Import button
        self.import_button = ctk.CTkButton(
            buttons_frame,
            text="📂 Import Config",
            command=self.import_config,
            height=35
        )
        self.import_button.pack(side="left")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            buttons_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="right")
    
    def create_section_header(self, parent, title):
        """Create a section header"""
        header_label = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(anchor="w", padx=20, pady=(20, 10))
    
    def create_setting_frame(self, parent):
        """Create a frame for a setting"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        return frame
    
    def create_setting_label(self, parent, text):
        """Create a setting label"""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=200
        )
        label.pack(side="left")
        return label
    
    def setup_layout(self):
        """Setup the layout"""
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pack all sections
        self.header_section.pack(fill="x", pady=(0, 10))
        self.general_section.pack(fill="x", pady=(0, 10))
        self.browser_section.pack(fill="x", pady=(0, 10))
        self.automation_section.pack(fill="x", pady=(0, 10))
        self.security_section.pack(fill="x", pady=(0, 10))
        self.performance_section.pack(fill="x", pady=(0, 10))
        self.advanced_section.pack(fill="x", pady=(0, 10))
        self.actions_section.pack(fill="x")
        
        # Bind change events
        self.bind_change_events()
    
    def bind_change_events(self):
        """Bind change events to mark settings as modified"""
        # This would be implemented to track changes
        pass
    
    def load_settings(self):
        """Load current settings into UI"""
        if not self.main_window.config:
            return
        
        config = self.main_window.config
        
        # General settings
        self.default_browser_menu.set(config.default_browser)
        self.log_level_menu.set(config.log_level)
        
        # Browser settings
        self.framework_menu.set(config.automation_framework)
        self.width_entry.insert(0, str(config.window_width))
        self.height_entry.insert(0, str(config.window_height))
        self.headless_var.set(config.headless)
        self.page_timeout_entry.insert(0, str(config.page_load_timeout))
        self.implicit_wait_entry.insert(0, str(config.implicit_wait))
        
        # Automation settings
        self.human_delays_var.set(config.human_like_delays)
        self.auto_scroll_var.set(config.auto_scroll)
        self.min_delay_entry.insert(0, str(config.min_delay))
        self.max_delay_entry.insert(0, str(config.max_delay))
        self.screenshot_error_var.set(config.screenshot_on_error)
        
        # Security settings
        self.allow_downloads_var.set(config.allow_file_downloads)
        self.allow_notifications_var.set(config.allow_notifications)
        self.allow_location_var.set(config.allow_location)
        self.allow_camera_var.set(config.allow_camera)
        self.allow_microphone_var.set(config.allow_microphone)
        self.use_container_var.set(config.use_container)
        
        # Performance settings
        self.plugins_enabled_var.set(config.plugins_enabled)
    
    def save_settings(self):
        """Save current settings to configuration"""
        try:
            config = self.main_window.config
            
            # General settings
            config.default_browser = self.default_browser_menu.get().lower()
            config.log_level = self.log_level_menu.get()
            
            # Browser settings
            config.automation_framework = self.framework_menu.get()
            config.window_width = int(self.width_entry.get() or "1920")
            config.window_height = int(self.height_entry.get() or "1080")
            config.headless = self.headless_var.get()
            config.page_load_timeout = int(self.page_timeout_entry.get() or "30")
            config.implicit_wait = int(self.implicit_wait_entry.get() or "10")
            
            # Automation settings
            config.human_like_delays = self.human_delays_var.get()
            config.auto_scroll = self.auto_scroll_var.get()
            config.min_delay = float(self.min_delay_entry.get() or "0.5")
            config.max_delay = float(self.max_delay_entry.get() or "2.0")
            config.screenshot_on_error = self.screenshot_error_var.get()
            
            # Security settings
            config.allow_file_downloads = self.allow_downloads_var.get()
            config.allow_notifications = self.allow_notifications_var.get()
            config.allow_location = self.allow_location_var.get()
            config.allow_camera = self.allow_camera_var.get()
            config.allow_microphone = self.allow_microphone_var.get()
            config.use_container = self.use_container_var.get()
            
            # Performance settings
            config.plugins_enabled = self.plugins_enabled_var.get()
            
            # Save to file
            self.save_config_to_file()
            
            self.show_status("Settings saved successfully!", "#4CAF50")
            self.settings_changed = False
            
        except Exception as e:
            self.main_window.show_error_dialog("Save Error", f"Failed to save settings: {str(e)}")
    
    def save_config_to_file(self):
        """Save configuration to file"""
        try:
            config_data = self.main_window.config.to_dict()
            
            # Remove sensitive data before saving
            sensitive_keys = ['openai_api_key', 'claude_api_key', 'gemini_api_key']
            for key in sensitive_keys:
                config_data.pop(key, None)
            
            with open("config.json", "w") as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        result = tk.messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values? This cannot be undone."
        )
        
        if result:
            # Create new default config
            from ..core.config import Config
            default_config = Config()
            
            # Update main window config
            self.main_window.config = default_config
            
            # Reload UI
            self.clear_all_inputs()
            self.load_settings()
            
            self.show_status("Settings reset to defaults", "#FF9800")
    
    def clear_all_inputs(self):
        """Clear all input fields"""
        # Clear entry widgets
        for widget in [self.width_entry, self.height_entry, self.page_timeout_entry, 
                      self.implicit_wait_entry, self.min_delay_entry, self.max_delay_entry,
                      self.max_memory_entry, self.max_concurrent_entry, self.user_agent_entry,
                      self.proxy_entry, self.config_path_entry]:
            widget.delete(0, "end")
    
    def export_config(self):
        """Export configuration to file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                title="Export Configuration",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                config_data = self.main_window.config.to_dict()
                
                with open(filename, 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                self.show_status(f"Configuration exported to {filename}", "#4CAF50")
                
        except Exception as e:
            self.main_window.show_error_dialog("Export Error", f"Failed to export configuration: {str(e)}")
    
    def import_config(self):
        """Import configuration from file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.askopenfilename(
                title="Import Configuration",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    config_data = json.load(f)
                
                # Update config
                from ..core.config import Config
                self.main_window.config = Config.from_dict(config_data)
                
                # Reload UI
                self.clear_all_inputs()
                self.load_settings()
                
                self.show_status(f"Configuration imported from {filename}", "#4CAF50")
                
        except Exception as e:
            self.main_window.show_error_dialog("Import Error", f"Failed to import configuration: {str(e)}")
    
    def browse_config_file(self):
        """Browse for configuration file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.askopenfilename(
                title="Select Configuration File",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                self.config_path_entry.delete(0, "end")
                self.config_path_entry.insert(0, filename)
                
        except Exception as e:
            self.main_window.show_error_dialog("Browse Error", f"Failed to browse for file: {str(e)}")
    
    def on_theme_change(self, value):
        """Handle theme change"""
        theme_map = {
            "Dark": "dark",
            "Light": "light", 
            "System": "system"
        }
        
        theme = theme_map.get(value, "dark")
        ctk.set_appearance_mode(theme)
        
        self.show_status("Theme changed. Restart may be required for full effect.", "#4CAF50")
    
    def show_status(self, message, color="#FFFFFF"):
        """Show status message"""
        self.status_label.configure(text=message, text_color=color)
        
        # Clear status after 3 seconds
        self.parent.after(3000, lambda: self.status_label.configure(text=""))