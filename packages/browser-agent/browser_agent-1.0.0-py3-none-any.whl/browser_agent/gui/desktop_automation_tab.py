import tkinter as tk
import customtkinter as ctk
import asyncio
import threading
from typing import Dict, Any, Optional
import pyautogui
from PIL import Image, ImageTk
import os

class DesktopAutomationTab:
    """Desktop Automation tab for the main GUI"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.desktop_automation = None
        
        # Initialize PyAutoGUI settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        self.create_widgets()
        self.setup_layout()
    
    def create_widgets(self):
        """Create all widgets for the desktop automation tab"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.parent)
        
        # Create sections
        self.create_control_section()
        self.create_mouse_section()
        self.create_keyboard_section()
        self.create_application_section()
        self.create_screen_section()
        self.create_output_section()
    
    def create_control_section(self):
        """Create the main control section"""
        self.control_frame = ctk.CTkFrame(self.main_frame)
        
        # Title
        title_label = ctk.CTkLabel(
            self.control_frame,
            text="🖥️ Desktop Automation Control",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Status
        self.status_label = ctk.CTkLabel(
            self.control_frame,
            text="Status: Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
        
        # Quick actions
        quick_frame = ctk.CTkFrame(self.control_frame)
        quick_frame.pack(fill="x", padx=10, pady=5)
        
        self.screenshot_btn = ctk.CTkButton(
            quick_frame,
            text="📸 Take Screenshot",
            command=self.take_screenshot
        )
        self.screenshot_btn.pack(side="left", padx=5, pady=5)
        
        self.get_mouse_pos_btn = ctk.CTkButton(
            quick_frame,
            text="🖱️ Get Mouse Position",
            command=self.get_mouse_position
        )
        self.get_mouse_pos_btn.pack(side="left", padx=5, pady=5)
        
        self.screen_info_btn = ctk.CTkButton(
            quick_frame,
            text="📊 Screen Info",
            command=self.get_screen_info
        )
        self.screen_info_btn.pack(side="left", padx=5, pady=5)
    
    def create_mouse_section(self):
        """Create mouse control section"""
        self.mouse_frame = ctk.CTkFrame(self.main_frame)
        
        # Title
        mouse_title = ctk.CTkLabel(
            self.mouse_frame,
            text="🖱️ Mouse Control",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        mouse_title.pack(pady=(10, 5))
        
        # Click coordinates
        coords_frame = ctk.CTkFrame(self.mouse_frame)
        coords_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(coords_frame, text="Click at coordinates:").pack(side="left", padx=5)
        
        self.x_entry = ctk.CTkEntry(coords_frame, placeholder_text="X", width=80)
        self.x_entry.pack(side="left", padx=2)
        
        self.y_entry = ctk.CTkEntry(coords_frame, placeholder_text="Y", width=80)
        self.y_entry.pack(side="left", padx=2)
        
        self.click_btn = ctk.CTkButton(
            coords_frame,
            text="Click",
            command=self.click_coordinates,
            width=80
        )
        self.click_btn.pack(side="left", padx=5)
        
        # Mouse movement
        move_frame = ctk.CTkFrame(self.mouse_frame)
        move_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(move_frame, text="Move mouse to:").pack(side="left", padx=5)
        
        self.move_x_entry = ctk.CTkEntry(move_frame, placeholder_text="X", width=80)
        self.move_x_entry.pack(side="left", padx=2)
        
        self.move_y_entry = ctk.CTkEntry(move_frame, placeholder_text="Y", width=80)
        self.move_y_entry.pack(side="left", padx=2)
        
        self.move_btn = ctk.CTkButton(
            move_frame,
            text="Move",
            command=self.move_mouse,
            width=80
        )
        self.move_btn.pack(side="left", padx=5)
        
        # Scroll
        scroll_frame = ctk.CTkFrame(self.mouse_frame)
        scroll_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(scroll_frame, text="Scroll:").pack(side="left", padx=5)
        
        self.scroll_up_btn = ctk.CTkButton(
            scroll_frame,
            text="↑ Up",
            command=lambda: self.scroll("up"),
            width=60
        )
        self.scroll_up_btn.pack(side="left", padx=2)
        
        self.scroll_down_btn = ctk.CTkButton(
            scroll_frame,
            text="↓ Down",
            command=lambda: self.scroll("down"),
            width=60
        )
        self.scroll_down_btn.pack(side="left", padx=2)
    
    def create_keyboard_section(self):
        """Create keyboard control section"""
        self.keyboard_frame = ctk.CTkFrame(self.main_frame)
        
        # Title
        keyboard_title = ctk.CTkLabel(
            self.keyboard_frame,
            text="⌨️ Keyboard Control",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        keyboard_title.pack(pady=(10, 5))
        
        # Type text
        type_frame = ctk.CTkFrame(self.keyboard_frame)
        type_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(type_frame, text="Type text:").pack(side="left", padx=5)
        
        self.text_entry = ctk.CTkEntry(type_frame, placeholder_text="Enter text to type", width=200)
        self.text_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        self.type_btn = ctk.CTkButton(
            type_frame,
            text="Type",
            command=self.type_text,
            width=80
        )
        self.type_btn.pack(side="left", padx=5)
        
        # Press keys
        key_frame = ctk.CTkFrame(self.keyboard_frame)
        key_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(key_frame, text="Press key:").pack(side="left", padx=5)
        
        self.key_entry = ctk.CTkEntry(key_frame, placeholder_text="Key name (e.g., enter, ctrl+c)", width=200)
        self.key_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        self.press_key_btn = ctk.CTkButton(
            key_frame,
            text="Press",
            command=self.press_key,
            width=80
        )
        self.press_key_btn.pack(side="left", padx=5)
        
        # Common keys
        common_frame = ctk.CTkFrame(self.keyboard_frame)
        common_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(common_frame, text="Common keys:").pack(side="left", padx=5)
        
        common_keys = ["enter", "tab", "space", "esc", "ctrl+c", "ctrl+v", "alt+tab"]
        for key in common_keys:
            btn = ctk.CTkButton(
                common_frame,
                text=key,
                command=lambda k=key: self.press_specific_key(k),
                width=60
            )
            btn.pack(side="left", padx=2)
    
    def create_application_section(self):
        """Create application control section"""
        self.app_frame = ctk.CTkFrame(self.main_frame)
        
        # Title
        app_title = ctk.CTkLabel(
            self.app_frame,
            text="📱 Application Control",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        app_title.pack(pady=(10, 5))
        
        # Open application
        open_frame = ctk.CTkFrame(self.app_frame)
        open_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(open_frame, text="Open application:").pack(side="left", padx=5)
        
        self.app_entry = ctk.CTkEntry(open_frame, placeholder_text="Application name or path", width=200)
        self.app_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        self.open_app_btn = ctk.CTkButton(
            open_frame,
            text="Open",
            command=self.open_application,
            width=80
        )
        self.open_app_btn.pack(side="left", padx=5)
        
        # Common applications
        common_apps_frame = ctk.CTkFrame(self.app_frame)
        common_apps_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(common_apps_frame, text="Quick launch:").pack(side="left", padx=5)
        
        common_apps = ["Calculator", "TextEdit", "Safari", "Finder", "Terminal"]
        for app in common_apps:
            btn = ctk.CTkButton(
                common_apps_frame,
                text=app,
                command=lambda a=app: self.open_specific_app(a),
                width=80
            )
            btn.pack(side="left", padx=2)
    
    def create_screen_section(self):
        """Create screen control section"""
        self.screen_frame = ctk.CTkFrame(self.main_frame)
        
        # Title
        screen_title = ctk.CTkLabel(
            self.screen_frame,
            text="📺 Screen Control",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        screen_title.pack(pady=(10, 5))
        
        # Screenshot preview
        self.screenshot_label = ctk.CTkLabel(
            self.screen_frame,
            text="Screenshot will appear here",
            width=300,
            height=200
        )
        self.screenshot_label.pack(pady=10)
        
        # Image template matching
        template_frame = ctk.CTkFrame(self.screen_frame)
        template_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(template_frame, text="Find and click image:").pack(side="left", padx=5)
        
        self.image_path_entry = ctk.CTkEntry(template_frame, placeholder_text="Image file path", width=200)
        self.image_path_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        self.browse_image_btn = ctk.CTkButton(
            template_frame,
            text="Browse",
            command=self.browse_image,
            width=80
        )
        self.browse_image_btn.pack(side="left", padx=2)
        
        self.click_image_btn = ctk.CTkButton(
            template_frame,
            text="Find & Click",
            command=self.find_and_click_image,
            width=100
        )
        self.click_image_btn.pack(side="left", padx=2)
    
    def create_output_section(self):
        """Create output/log section"""
        self.output_frame = ctk.CTkFrame(self.main_frame)
        
        # Title
        output_title = ctk.CTkLabel(
            self.output_frame,
            text="📝 Output Log",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        output_title.pack(pady=(10, 5))
        
        # Output text area
        self.output_text = ctk.CTkTextbox(
            self.output_frame,
            height=150,
            wrap="word"
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Clear button
        self.clear_btn = ctk.CTkButton(
            self.output_frame,
            text="Clear Log",
            command=self.clear_output
        )
        self.clear_btn.pack(pady=5)
    
    def setup_layout(self):
        """Setup the layout of all sections"""
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pack sections in order
        self.control_frame.pack(fill="x", pady=5)
        
        # Create two columns for mouse/keyboard and app/screen
        columns_frame = ctk.CTkFrame(self.main_frame)
        columns_frame.pack(fill="both", expand=True, pady=5)
        
        left_column = ctk.CTkFrame(columns_frame)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        right_column = ctk.CTkFrame(columns_frame)
        right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Reparent sections to columns
        self.mouse_frame.pack_forget()
        self.keyboard_frame.pack_forget()
        self.app_frame.pack_forget()
        self.screen_frame.pack_forget()
        
        self.mouse_frame = ctk.CTkFrame(left_column)
        self.keyboard_frame = ctk.CTkFrame(left_column)
        self.app_frame = ctk.CTkFrame(right_column)
        self.screen_frame = ctk.CTkFrame(right_column)
        
        # Recreate sections in new frames
        self.create_mouse_section()
        self.create_keyboard_section()
        self.create_application_section()
        self.create_screen_section()
        
        self.mouse_frame.pack(fill="x", pady=5)
        self.keyboard_frame.pack(fill="x", pady=5)
        self.app_frame.pack(fill="x", pady=5)
        self.screen_frame.pack(fill="both", expand=True, pady=5)
        
        self.output_frame.pack(fill="x", pady=5)
    
    def log_output(self, message: str):
        """Add message to output log"""
        self.output_text.insert("end", f"{message}\n")
        self.output_text.see("end")
    
    def clear_output(self):
        """Clear the output log"""
        self.output_text.delete("1.0", "end")
    
    def update_status(self, status: str):
        """Update status label"""
        self.status_label.configure(text=f"Status: {status}")
    
    # Desktop automation methods
    def take_screenshot(self):
        """Take a screenshot"""
        try:
            self.update_status("Taking screenshot...")
            screenshot = pyautogui.screenshot()
            
            # Save screenshot
            screenshot_path = "desktop_screenshot.png"
            screenshot.save(screenshot_path)
            
            # Display thumbnail
            thumbnail = screenshot.resize((300, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(thumbnail)
            self.screenshot_label.configure(image=photo, text="")
            self.screenshot_label.image = photo  # Keep a reference
            
            self.log_output(f"Screenshot saved: {screenshot_path}")
            self.update_status("Screenshot taken")
            
        except Exception as e:
            self.log_output(f"Error taking screenshot: {str(e)}")
            self.update_status("Error")
    
    def get_mouse_position(self):
        """Get current mouse position"""
        try:
            x, y = pyautogui.position()
            self.log_output(f"Mouse position: ({x}, {y})")
            self.x_entry.delete(0, "end")
            self.x_entry.insert(0, str(x))
            self.y_entry.delete(0, "end")
            self.y_entry.insert(0, str(y))
            self.update_status(f"Mouse at ({x}, {y})")
        except Exception as e:
            self.log_output(f"Error getting mouse position: {str(e)}")
            self.update_status("Error")
    
    def get_screen_info(self):
        """Get screen information"""
        try:
            size = pyautogui.size()
            self.log_output(f"Screen size: {size.width} x {size.height}")
            self.update_status(f"Screen: {size.width}x{size.height}")
        except Exception as e:
            self.log_output(f"Error getting screen info: {str(e)}")
            self.update_status("Error")
    
    def click_coordinates(self):
        """Click at specified coordinates"""
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            
            self.update_status(f"Clicking at ({x}, {y})...")
            pyautogui.click(x, y)
            
            self.log_output(f"Clicked at ({x}, {y})")
            self.update_status("Click completed")
            
        except ValueError:
            self.log_output("Error: Please enter valid coordinates")
            self.update_status("Error")
        except Exception as e:
            self.log_output(f"Error clicking: {str(e)}")
            self.update_status("Error")
    
    def move_mouse(self):
        """Move mouse to specified coordinates"""
        try:
            x = int(self.move_x_entry.get())
            y = int(self.move_y_entry.get())
            
            self.update_status(f"Moving mouse to ({x}, {y})...")
            pyautogui.moveTo(x, y, duration=0.5)
            
            self.log_output(f"Mouse moved to ({x}, {y})")
            self.update_status("Move completed")
            
        except ValueError:
            self.log_output("Error: Please enter valid coordinates")
            self.update_status("Error")
        except Exception as e:
            self.log_output(f"Error moving mouse: {str(e)}")
            self.update_status("Error")
    
    def scroll(self, direction: str):
        """Scroll mouse wheel"""
        try:
            clicks = 3 if direction == "up" else -3
            pyautogui.scroll(clicks)
            
            self.log_output(f"Scrolled {direction}")
            self.update_status(f"Scrolled {direction}")
            
        except Exception as e:
            self.log_output(f"Error scrolling: {str(e)}")
            self.update_status("Error")
    
    def type_text(self):
        """Type the specified text"""
        try:
            text = self.text_entry.get()
            if not text:
                self.log_output("Error: Please enter text to type")
                return
            
            self.update_status("Typing text...")
            pyautogui.typewrite(text, interval=0.05)
            
            self.log_output(f"Typed: {text}")
            self.update_status("Text typed")
            
        except Exception as e:
            self.log_output(f"Error typing text: {str(e)}")
            self.update_status("Error")
    
    def press_key(self):
        """Press the specified key"""
        try:
            key = self.key_entry.get()
            if not key:
                self.log_output("Error: Please enter a key to press")
                return
            
            self.update_status(f"Pressing key: {key}")
            
            # Handle key combinations
            if '+' in key:
                keys = key.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key)
            
            self.log_output(f"Pressed key: {key}")
            self.update_status("Key pressed")
            
        except Exception as e:
            self.log_output(f"Error pressing key: {str(e)}")
            self.update_status("Error")
    
    def press_specific_key(self, key: str):
        """Press a specific key"""
        try:
            self.update_status(f"Pressing key: {key}")
            
            # Handle key combinations
            if '+' in key:
                keys = key.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key)
            
            self.log_output(f"Pressed key: {key}")
            self.update_status("Key pressed")
            
        except Exception as e:
            self.log_output(f"Error pressing key: {str(e)}")
            self.update_status("Error")
    
    def open_application(self):
        """Open the specified application"""
        try:
            app_name = self.app_entry.get()
            if not app_name:
                self.log_output("Error: Please enter an application name")
                return
            
            self.update_status(f"Opening {app_name}...")
            
            # Use system-specific commands
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", "-a", app_name])
            elif system == "Windows":
                subprocess.run(["start", app_name], shell=True)
            else:  # Linux
                subprocess.run([app_name])
            
            self.log_output(f"Opened application: {app_name}")
            self.update_status("Application opened")
            
        except Exception as e:
            self.log_output(f"Error opening application: {str(e)}")
            self.update_status("Error")
    
    def open_specific_app(self, app_name: str):
        """Open a specific application"""
        self.app_entry.delete(0, "end")
        self.app_entry.insert(0, app_name)
        self.open_application()
    
    def browse_image(self):
        """Browse for an image file"""
        try:
            from tkinter import filedialog
            
            file_path = filedialog.askopenfilename(
                title="Select Image File",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
            )
            
            if file_path:
                self.image_path_entry.delete(0, "end")
                self.image_path_entry.insert(0, file_path)
                self.log_output(f"Selected image: {file_path}")
                
        except Exception as e:
            self.log_output(f"Error browsing for image: {str(e)}")
    
    def find_and_click_image(self):
        """Find and click on an image on the screen"""
        try:
            image_path = self.image_path_entry.get()
            if not image_path or not os.path.exists(image_path):
                self.log_output("Error: Please select a valid image file")
                return
            
            self.update_status("Searching for image...")
            
            # Find the image on screen
            location = pyautogui.locateOnScreen(image_path, confidence=0.8)
            
            if location:
                # Click the center of the found image
                center = pyautogui.center(location)
                pyautogui.click(center)
                
                self.log_output(f"Found and clicked image at {center}")
                self.update_status("Image clicked")
            else:
                self.log_output("Image not found on screen")
                self.update_status("Image not found")
                
        except Exception as e:
            self.log_output(f"Error finding/clicking image: {str(e)}")
            self.update_status("Error")