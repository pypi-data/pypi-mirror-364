"""
Enhanced Browser Tab with Comprehensive Support Detection and User Guidance

This module provides an improved browser management interface with:
- Comprehensive browser support detection
- Clear installation guidance
- Visual feedback and error handling
- Real-time session monitoring
- Troubleshooting assistance
"""

import tkinter as tk
import customtkinter as ctk
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime

from ..browsers.detector import BrowserDetector
from ..browsers.support import get_browser_support_manager, BrowserSupport


class EnhancedBrowserTab:
    """Enhanced browser control interface with comprehensive support"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.browser_detector = BrowserDetector()
        self.support_manager = get_browser_support_manager()
        self.available_browsers = {}
        self.current_browser = None
        self.session_monitor_running = False
        
        # UI state tracking
        self.selected_browser_buttons = {}
        self.browser_status_labels = {}
        
        self.create_widgets()
        self.setup_layout()
        self.refresh_browsers()
        self.start_session_monitor()
    
    def create_widgets(self):
        """Create enhanced browser tab widgets"""
        # Main scrollable container
        self.main_container = ctk.CTkScrollableFrame(self.parent)
        
        # Browser support overview
        self.support_section = ctk.CTkFrame(self.main_container)
        self.create_support_overview()
        
        # Browser detection and selection
        self.browser_section = ctk.CTkFrame(self.main_container)
        self.create_browser_selection()
        
        # Installation guidance
        self.guidance_section = ctk.CTkFrame(self.main_container)
        self.create_installation_guidance()
        
        # Session monitoring
        self.session_section = ctk.CTkFrame(self.main_container)
        self.create_session_monitoring()
        
        # Browser controls
        self.control_section = ctk.CTkFrame(self.main_container)
        self.create_browser_controls()
        
        # Troubleshooting section
        self.troubleshoot_section = ctk.CTkFrame(self.main_container)
        self.create_troubleshooting_section()
    
    def create_support_overview(self):
        """Create browser support overview section"""
        # Header
        header_label = ctk.CTkLabel(
            self.support_section,
            text="🌐 Browser Support Matrix",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Support matrix frame
        self.support_matrix_frame = ctk.CTkFrame(self.support_section)
        self.support_matrix_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Create support matrix headers
        headers_frame = ctk.CTkFrame(self.support_matrix_frame, fg_color="transparent")
        headers_frame.pack(fill="x", padx=10, pady=10)
        
        headers = ["Browser", "Status", "Selenium", "Playwright", "Support Level", "Action"]
        header_weights = [2, 1, 1, 1, 2, 2]
        
        for i, (header, weight) in enumerate(zip(headers, header_weights)):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            label.grid(row=0, column=i, padx=5, sticky="ew")
            headers_frame.grid_columnconfigure(i, weight=weight)
        
        # Support matrix content will be populated by refresh_browsers()
        self.support_content_frame = ctk.CTkFrame(self.support_matrix_frame, fg_color="transparent")
        self.support_content_frame.pack(fill="x", padx=10, pady=(0, 10))
    
    def create_browser_selection(self):
        """Create enhanced browser selection interface"""
        # Header
        selection_header = ctk.CTkLabel(
            self.browser_section,
            text="🎯 Browser Selection",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        selection_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Detection controls
        detection_frame = ctk.CTkFrame(self.browser_section, fg_color="transparent")
        detection_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.refresh_button = ctk.CTkButton(
            detection_frame,
            text="🔄 Refresh Detection",
            command=self.refresh_browsers,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        self.refresh_button.pack(side="left")
        
        self.detection_status = ctk.CTkLabel(
            detection_frame,
            text="Detecting browsers...",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        self.detection_status.pack(side="left", padx=(10, 0))
        
        # Browser selection grid
        self.browser_grid_frame = ctk.CTkFrame(self.browser_section)
        self.browser_grid_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    def create_installation_guidance(self):
        """Create installation guidance section"""
        # Header
        guidance_header = ctk.CTkLabel(
            self.guidance_section,
            text="📋 Installation Guidance",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        guidance_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Guidance content
        self.guidance_text = ctk.CTkTextbox(
            self.guidance_section,
            height=120,
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        self.guidance_text.pack(fill="x", padx=20, pady=(0, 20))
    
    def create_session_monitoring(self):
        """Create session monitoring section"""
        # Header
        session_header = ctk.CTkLabel(
            self.session_section,
            text="📊 Session Monitoring",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        session_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Session status grid
        status_grid = ctk.CTkFrame(self.session_section, fg_color="transparent")
        status_grid.pack(fill="x", padx=20, pady=(0, 10))
        
        # Session status indicators
        self.session_indicators = {}
        indicators = [
            ("Session Active", "session_active"),
            ("Browser Health", "browser_health"),
            ("Last Activity", "last_activity"),
            ("Framework", "framework")
        ]
        
        for i, (label, key) in enumerate(indicators):
            row = i // 2
            col = i % 2
            
            indicator_frame = ctk.CTkFrame(status_grid)
            indicator_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            status_grid.grid_columnconfigure(col, weight=1)
            
            label_widget = ctk.CTkLabel(
                indicator_frame,
                text=label,
                font=ctk.CTkFont(size=11, weight="bold")
            )
            label_widget.pack(pady=(10, 5))
            
            value_widget = ctk.CTkLabel(
                indicator_frame,
                text="N/A",
                font=ctk.CTkFont(size=10),
                text_color="#666666"
            )
            value_widget.pack(pady=(0, 10))
            
            self.session_indicators[key] = {
                'label': label_widget,
                'value': value_widget,
                'frame': indicator_frame
            }
    
    def create_browser_controls(self):
        """Create browser control interface"""
        # Header
        control_header = ctk.CTkLabel(
            self.control_section,
            text="🎮 Browser Controls",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        control_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Control buttons
        controls_frame = ctk.CTkFrame(self.control_section, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Launch/Close buttons
        self.launch_button = ctk.CTkButton(
            controls_frame,
            text="🚀 Launch Browser",
            command=self.launch_browser,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            state="disabled"
        )
        self.launch_button.pack(side="left", padx=(0, 10))
        
        self.close_button = ctk.CTkButton(
            controls_frame,
            text="⏹️ Close Browser",
            command=self.close_browser,
            font=ctk.CTkFont(size=12),
            height=40,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            state="disabled"
        )
        self.close_button.pack(side="left", padx=(0, 10))
        
        # Framework selector
        framework_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        framework_frame.pack(side="right")
        
        framework_label = ctk.CTkLabel(
            framework_frame,
            text="Framework:",
            font=ctk.CTkFont(size=11)
        )
        framework_label.pack(side="left", padx=(0, 5))
        
        self.framework_selector = ctk.CTkOptionMenu(
            framework_frame,
            values=["Selenium", "Playwright"],
            command=self.on_framework_change,
            width=120,
            height=30
        )
        self.framework_selector.pack(side="left")
        
        # Browser settings
        settings_frame = ctk.CTkFrame(self.control_section, fg_color="transparent")
        settings_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Headless mode toggle
        self.headless_var = ctk.BooleanVar()
        self.headless_checkbox = ctk.CTkCheckBox(
            settings_frame,
            text="Headless Mode",
            variable=self.headless_var,
            font=ctk.CTkFont(size=11)
        )
        self.headless_checkbox.pack(side="left", padx=(0, 20))
        
        # Auto-detect toggle
        self.auto_detect_var = ctk.BooleanVar(value=True)
        self.auto_detect_checkbox = ctk.CTkCheckBox(
            settings_frame,
            text="Auto-detect browsers",
            variable=self.auto_detect_var,
            command=self.on_auto_detect_change,
            font=ctk.CTkFont(size=11)
        )
        self.auto_detect_checkbox.pack(side="left")
    
    def create_troubleshooting_section(self):
        """Create troubleshooting and help section"""
        # Header
        trouble_header = ctk.CTkLabel(
            self.troubleshoot_section,
            text="🔧 Troubleshooting",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        trouble_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Troubleshooting controls
        trouble_controls = ctk.CTkFrame(self.troubleshoot_section, fg_color="transparent")
        trouble_controls.pack(fill="x", padx=20, pady=(0, 10))
        
        self.health_check_button = ctk.CTkButton(
            trouble_controls,
            text="🏥 Health Check",
            command=self.run_health_check,
            font=ctk.CTkFont(size=11),
            height=30
        )
        self.health_check_button.pack(side="left", padx=(0, 10))
        
        self.force_cleanup_button = ctk.CTkButton(
            trouble_controls,
            text="🧹 Force Cleanup",
            command=self.force_cleanup,
            font=ctk.CTkFont(size=11),
            height=30,
            fg_color="#f39c12",
            hover_color="#e67e22"
        )
        self.force_cleanup_button.pack(side="left", padx=(0, 10))
        
        self.show_guide_button = ctk.CTkButton(
            trouble_controls,
            text="📖 Show Guide",
            command=self.show_troubleshooting_guide,
            font=ctk.CTkFont(size=11),
            height=30
        )
        self.show_guide_button.pack(side="left")
        
        # Status display
        self.troubleshoot_text = ctk.CTkTextbox(
            self.troubleshoot_section,
            height=100,
            font=ctk.CTkFont(size=10),
            wrap="word"
        )
        self.troubleshoot_text.pack(fill="x", padx=20, pady=(0, 20))
    
    def setup_layout(self):
        """Setup the layout of browser tab"""
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pack sections in order
        self.support_section.pack(fill="x", pady=(0, 10))
        self.browser_section.pack(fill="x", pady=(0, 10))
        self.guidance_section.pack(fill="x", pady=(0, 10))
        self.session_section.pack(fill="x", pady=(0, 10))
        self.control_section.pack(fill="x", pady=(0, 10))
        self.troubleshoot_section.pack(fill="x", pady=(0, 10))
    
    def refresh_browsers(self):
        """Refresh browser detection with enhanced feedback"""
        def detect_browsers():
            try:
                self.update_detection_status("🔍 Detecting browsers...")
                
                # Clear previous browser buttons
                for widget in self.browser_grid_frame.winfo_children():
                    widget.destroy()
                
                # Detect available browsers
                self.available_browsers = self.browser_detector.detect_all()
                
                # Get browser recommendations
                recommendations = self.main_window.browser_manager.get_browser_recommendations() if hasattr(self.main_window, 'browser_manager') else None
                
                # Update support matrix
                self.update_support_matrix()
                
                # Create browser selection buttons
                self.create_browser_buttons()
                
                # Update installation guidance
                self.update_installation_guidance(recommendations)
                
                if self.available_browsers:
                    self.update_detection_status(f"✅ Found {len(self.available_browsers)} browser(s)")
                else:
                    self.update_detection_status("❌ No supported browsers found")
                    
            except Exception as e:
                self.update_detection_status(f"❌ Detection failed: {str(e)}")
        
        # Run detection in background
        threading.Thread(target=detect_browsers, daemon=True).start()
    
    def update_support_matrix(self):
        """Update the browser support matrix display"""
        # Clear existing content
        for widget in self.support_content_frame.winfo_children():
            widget.destroy()
        
        supported_browsers = self.support_manager.get_supported_browsers()
        
        for i, (name, browser_info) in enumerate(supported_browsers.items()):
            is_installed = name in self.available_browsers
            
            # Browser row frame
            row_frame = ctk.CTkFrame(self.support_content_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            # Configure grid
            for j in range(6):
                row_frame.grid_columnconfigure(j, weight=[2, 1, 1, 1, 2, 2][j])
            
            # Browser name
            name_label = ctk.CTkLabel(
                row_frame,
                text=browser_info.display_name,
                font=ctk.CTkFont(size=11, weight="bold")
            )
            name_label.grid(row=0, column=0, padx=5, sticky="w")
            
            # Installation status
            status_color = "#2ecc71" if is_installed else "#e74c3c"
            status_text = "✅ Installed" if is_installed else "❌ Missing"
            status_label = ctk.CTkLabel(
                row_frame,
                text=status_text,
                font=ctk.CTkFont(size=10),
                text_color=status_color
            )
            status_label.grid(row=0, column=1, padx=5)
            
            # Selenium support
            selenium_text = "✅" if browser_info.selenium_support else "❌"
            selenium_label = ctk.CTkLabel(
                row_frame,
                text=selenium_text,
                font=ctk.CTkFont(size=10)
            )
            selenium_label.grid(row=0, column=2, padx=5)
            
            # Playwright support
            playwright_text = "✅" if browser_info.playwright_support else "❌"
            playwright_label = ctk.CTkLabel(
                row_frame,
                text=playwright_text,
                font=ctk.CTkFont(size=10)
            )
            playwright_label.grid(row=0, column=3, padx=5)
            
            # Support level
            support_colors = {
                BrowserSupport.RECOMMENDED: "#2ecc71",
                BrowserSupport.FULLY_SUPPORTED: "#3498db",
                BrowserSupport.PARTIALLY_SUPPORTED: "#f39c12",
                BrowserSupport.NOT_SUPPORTED: "#e74c3c"
            }
            support_text = browser_info.support_level.value.replace("_", " ").title()
            support_color = support_colors.get(browser_info.support_level, "#666666")
            
            support_label = ctk.CTkLabel(
                row_frame,
                text=support_text,
                font=ctk.CTkFont(size=10),
                text_color=support_color
            )
            support_label.grid(row=0, column=4, padx=5)
            
            # Action button
            if is_installed:
                action_button = ctk.CTkButton(
                    row_frame,
                    text="Select",
                    command=lambda b=name: self.select_browser(b),
                    font=ctk.CTkFont(size=10),
                    height=25,
                    width=80
                )
            else:
                action_button = ctk.CTkButton(
                    row_frame,
                    text="Install",
                    command=lambda b=name: self.show_installation_guide(b),
                    font=ctk.CTkFont(size=10),
                    height=25,
                    width=80,
                    fg_color="#f39c12",
                    hover_color="#e67e22"
                )
            
            action_button.grid(row=0, column=5, padx=5)
    
    def create_browser_buttons(self):
        """Create browser selection buttons"""
        if not self.available_browsers:
            no_browsers_label = ctk.CTkLabel(
                self.browser_grid_frame,
                text="No supported browsers detected.",
                font=ctk.CTkFont(size=12),
                text_color="#e74c3c"
            )
            no_browsers_label.pack(pady=20)
            return
        
        # Create buttons for available browsers
        for i, (name, browser_info) in enumerate(self.available_browsers.items()):
            row = i // 3
            col = i % 3
            
            # Browser button frame
            button_frame = ctk.CTkFrame(self.browser_grid_frame)
            button_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            # Configure grid
            self.browser_grid_frame.grid_columnconfigure(col, weight=1)
            
            # Browser button
            browser_button = ctk.CTkButton(
                button_frame,
                text=f"{browser_info.name.title()}",
                command=lambda b=name: self.select_browser(b),
                font=ctk.CTkFont(size=12, weight="bold"),
                height=40
            )
            browser_button.pack(fill="x", padx=10, pady=(10, 5))
            
            # Browser info
            info_text = f"Version: {browser_info.version or 'Unknown'}"
            info_label = ctk.CTkLabel(
                button_frame,
                text=info_text,
                font=ctk.CTkFont(size=10),
                text_color="#666666"
            )
            info_label.pack(pady=(0, 10))
            
            # Store button reference
            self.selected_browser_buttons[name] = browser_button
    
    def update_installation_guidance(self, recommendations):
        """Update installation guidance section"""
        if not recommendations:
            guidance_text = "✅ All recommended browsers are available!"
        else:
            guidance_text = recommendations.get('installation_guide', 'No guidance available')
        
        self.guidance_text.delete("1.0", "end")
        self.guidance_text.insert("1.0", guidance_text)
    
    def select_browser(self, browser_name):
        """Select a browser for automation"""
        # Update button states
        for name, button in self.selected_browser_buttons.items():
            if name == browser_name:
                button.configure(fg_color="#2ecc71", hover_color="#27ae60")
                button.configure(text=f"✓ {name.title()}")
            else:
                # Reset to default color
                button.configure(fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])
                button.configure(text=name.title())
        
        self.current_browser = browser_name
        self.launch_button.configure(state="normal")
        
        # Update status
        self.update_detection_status(f"✅ Selected: {browser_name.title()}")
    
    def launch_browser(self):
        """Launch the selected browser"""
        if not self.current_browser:
            self.show_error("No browser selected")
            return
        
        def launch_worker():
            try:
                self.update_launch_status("🚀 Launching browser...")
                
                # Get browser manager from main window
                if hasattr(self.main_window, 'browser_manager'):
                    browser_manager = self.main_window.browser_manager
                    
                    # Set headless mode
                    browser_manager.headless = self.headless_var.get()
                    
                    # Launch browser
                    driver = browser_manager.launch_browser(self.current_browser)
                    
                    if driver:
                        self.update_launch_status(f"✅ {self.current_browser.title()} launched successfully")
                        self.launch_button.configure(state="disabled")
                        self.close_button.configure(state="normal")
                    else:
                        self.update_launch_status("❌ Failed to launch browser")
                        
                else:
                    self.update_launch_status("❌ Browser manager not available")
                    
            except Exception as e:
                error_msg = str(e)
                self.update_launch_status(f"❌ Launch failed: {error_msg}")
                
                # Show troubleshooting guide
                if self.current_browser:
                    guide = self.support_manager.get_troubleshooting_guide(self.current_browser, error_msg)
                    self.troubleshoot_text.delete("1.0", "end")
                    self.troubleshoot_text.insert("1.0", guide)
        
        # Run in background
        threading.Thread(target=launch_worker, daemon=True).start()
    
    def close_browser(self):
        """Close the active browser"""
        def close_worker():
            try:
                self.update_launch_status("⏹️ Closing browser...")
                
                if hasattr(self.main_window, 'browser_manager'):
                    self.main_window.browser_manager.close_browser()
                    self.update_launch_status("✅ Browser closed successfully")
                else:
                    self.update_launch_status("❌ Browser manager not available")
                    
                self.launch_button.configure(state="normal")
                self.close_button.configure(state="disabled")
                
            except Exception as e:
                self.update_launch_status(f"❌ Close failed: {str(e)}")
        
        threading.Thread(target=close_worker, daemon=True).start()
    
    def start_session_monitor(self):
        """Start monitoring browser session"""
        def monitor_worker():
            self.session_monitor_running = True
            
            while self.session_monitor_running:
                try:
                    if hasattr(self.main_window, 'browser_manager'):
                        health = self.main_window.browser_manager.health_check()
                        self.update_session_indicators(health)
                    
                    time.sleep(2)  # Update every 2 seconds
                except Exception:
                    pass
        
        threading.Thread(target=monitor_worker, daemon=True).start()
    
    def update_session_indicators(self, health_data):
        """Update session monitoring indicators"""
        try:
            # Session active
            session_active = health_data.get('session_active', False)
            self.session_indicators['session_active']['value'].configure(
                text="🟢 Active" if session_active else "🔴 Inactive",
                text_color="#2ecc71" if session_active else "#e74c3c"
            )
            
            # Browser health
            has_timeout = health_data.get('session_timeout', False)
            health_text = "🟡 Timeout" if has_timeout else ("🟢 Healthy" if session_active else "⚪ Idle")
            health_color = "#f39c12" if has_timeout else ("#2ecc71" if session_active else "#666666")
            self.session_indicators['browser_health']['value'].configure(
                text=health_text,
                text_color=health_color
            )
            
            # Last activity
            last_activity = health_data.get('last_activity', 0)
            if last_activity:
                activity_time = datetime.fromtimestamp(last_activity).strftime("%H:%M:%S")
            else:
                activity_time = "N/A"
            self.session_indicators['last_activity']['value'].configure(text=activity_time)
            
            # Framework
            framework = health_data.get('framework', 'N/A').title()
            self.session_indicators['framework']['value'].configure(text=framework)
            
        except Exception:
            pass
    
    def run_health_check(self):
        """Run comprehensive health check"""
        def health_worker():
            try:
                self.troubleshoot_text.delete("1.0", "end")
                self.troubleshoot_text.insert("1.0", "🏥 Running health check...\n\n")
                
                if hasattr(self.main_window, 'browser_manager'):
                    health = self.main_window.browser_manager.health_check()
                    
                    # Format health report
                    report = "🏥 Browser Agent Health Report\n"
                    report += "=" * 35 + "\n\n"
                    
                    report += f"Session Status: {'🟢 Active' if health['session_active'] else '🔴 Inactive'}\n"
                    report += f"Available Browsers: {health['available_browsers']}\n"
                    report += f"Framework: {health['framework'].title()}\n"
                    
                    if health.get('current_url'):
                        report += f"Current URL: {health['current_url']}\n"
                    
                    if health.get('session_error'):
                        report += f"\n❌ Error: {health['session_error']}\n"
                    
                    # Recommendations
                    recommendations = health.get('recommendations', {})
                    if recommendations.get('missing_browsers'):
                        report += f"\n📋 Missing Browsers: {', '.join(recommendations['missing_browsers'])}\n"
                    
                    report += f"\n⏰ Last Activity: {datetime.fromtimestamp(health['last_activity']).strftime('%Y-%m-%d %H:%M:%S') if health['last_activity'] else 'N/A'}"
                    
                    self.troubleshoot_text.delete("1.0", "end")
                    self.troubleshoot_text.insert("1.0", report)
                    
                else:
                    self.troubleshoot_text.insert("end", "❌ Browser manager not available\n")
                    
            except Exception as e:
                self.troubleshoot_text.insert("end", f"❌ Health check failed: {str(e)}\n")
        
        threading.Thread(target=health_worker, daemon=True).start()
    
    def force_cleanup(self):
        """Force cleanup of browser processes"""
        def cleanup_worker():
            try:
                self.troubleshoot_text.delete("1.0", "end")
                self.troubleshoot_text.insert("1.0", "🧹 Performing force cleanup...\n\n")
                
                if hasattr(self.main_window, 'browser_manager'):
                    self.main_window.browser_manager.force_cleanup()
                    self.troubleshoot_text.insert("end", "✅ Force cleanup completed\n")
                    self.troubleshoot_text.insert("end", "🔄 Refreshing browser detection...\n")
                    
                    # Refresh browser detection
                    self.refresh_browsers()
                    
                    # Reset UI state
                    self.launch_button.configure(state="disabled")
                    self.close_button.configure(state="disabled")
                    
                else:
                    self.troubleshoot_text.insert("end", "❌ Browser manager not available\n")
                    
            except Exception as e:
                self.troubleshoot_text.insert("end", f"❌ Cleanup failed: {str(e)}\n")
        
        threading.Thread(target=cleanup_worker, daemon=True).start()
    
    def show_troubleshooting_guide(self):
        """Show comprehensive troubleshooting guide"""
        browser = self.current_browser or 'chrome'
        guide = self.support_manager.get_troubleshooting_guide(browser)
        
        self.troubleshoot_text.delete("1.0", "end")
        self.troubleshoot_text.insert("1.0", guide)
    
    def show_installation_guide(self, browser_name):
        """Show installation guide for a specific browser"""
        guide = self.support_manager.get_installation_guide(browser_name)
        if guide:
            self.guidance_text.delete("1.0", "end")
            self.guidance_text.insert("1.0", f"📋 Installation Guide for {browser_name.title()}:\n\n{guide}")
    
    def on_framework_change(self, framework):
        """Handle framework selection change"""
        if hasattr(self.main_window, 'browser_manager'):
            framework_lower = framework.lower()
            self.main_window.browser_manager.switch_framework(framework_lower)
            self.update_detection_status(f"🔄 Switched to {framework}")
    
    def on_auto_detect_change(self):
        """Handle auto-detect setting change"""
        if self.auto_detect_var.get():
            self.refresh_browsers()
    
    def update_detection_status(self, message):
        """Update detection status message"""
        try:
            self.detection_status.configure(text=message)
        except:
            pass
    
    def update_launch_status(self, message):
        """Update launch status message"""
        try:
            self.troubleshoot_text.delete("1.0", "end")
            self.troubleshoot_text.insert("1.0", message)
        except:
            pass
    
    def show_error(self, message):
        """Show error message"""
        self.update_launch_status(f"❌ Error: {message}")
    
    def cleanup(self):
        """Cleanup resources when tab is closed"""
        self.session_monitor_running = False