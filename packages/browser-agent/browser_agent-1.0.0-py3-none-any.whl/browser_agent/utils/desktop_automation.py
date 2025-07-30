import asyncio
import os
import time
import random
import cv2
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Union
import pyautogui
from PIL import Image, ImageDraw
import subprocess
import platform

from ..core.config import Config


class DesktopAutomation:
    """Desktop automation utilities using PyAutoGUI for system-wide control"""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Configure PyAutoGUI settings
        pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort
        pyautogui.PAUSE = 0.1 if config.human_like_delays else 0.05
        
        # Create screenshots directory
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Get screen size
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Platform-specific settings
        self.platform = platform.system().lower()
        
    async def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, Any]:
        """Take a screenshot of the screen or a specific region"""
        try:
            timestamp = int(time.time())
            filename = f"desktop_screenshot_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            screenshot.save(filepath)
            
            return {
                'success': True,
                'filepath': filepath,
                'size': screenshot.size,
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def click_at_coordinates(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> Dict[str, Any]:
        """Click at specific screen coordinates"""
        try:
            # Validate coordinates
            if not (0 <= x <= self.screen_width and 0 <= y <= self.screen_height):
                return {
                    'success': False,
                    'error': f"Coordinates ({x}, {y}) are outside screen bounds ({self.screen_width}x{self.screen_height})"
                }
            
            # Human-like movement
            if self.config.human_like_delays:
                # Move to position with slight randomness
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
                pyautogui.moveTo(x + offset_x, y + offset_y, duration=random.uniform(0.1, 0.3))
                await asyncio.sleep(random.uniform(0.05, 0.15))
            
            # Perform click
            pyautogui.click(x, y, clicks=clicks, button=button)
            
            return {
                'success': True,
                'coordinates': (x, y),
                'button': button,
                'clicks': clicks
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def find_and_click_image(self, image_path: str, confidence: float = 0.8, region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, Any]:
        """Find an image on screen and click it"""
        try:
            # Locate the image on screen
            location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
            
            if location is None:
                return {
                    'success': False,
                    'error': f"Image not found on screen: {image_path}"
                }
            
            # Get center coordinates
            center_x, center_y = pyautogui.center(location)
            
            # Click at the center
            result = await self.click_at_coordinates(center_x, center_y)
            
            if result['success']:
                result['image_location'] = location
                result['image_path'] = image_path
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def type_text(self, text: str, interval: Optional[float] = None) -> Dict[str, Any]:
        """Type text using the keyboard"""
        try:
            if interval is None:
                interval = random.uniform(0.05, 0.1) if self.config.human_like_delays else 0.01
            
            # Type the text
            pyautogui.typewrite(text, interval=interval)
            
            return {
                'success': True,
                'text': text,
                'length': len(text)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def press_key(self, key: str, presses: int = 1) -> Dict[str, Any]:
        """Press a specific key or key combination"""
        try:
            # Handle key combinations (e.g., 'ctrl+c', 'cmd+v')
            if '+' in key:
                keys = key.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key, presses=presses)
            
            return {
                'success': True,
                'key': key,
                'presses': presses
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
        """Scroll at current mouse position or specific coordinates"""
        try:
            if x is not None and y is not None:
                pyautogui.scroll(clicks, x=x, y=y)
            else:
                pyautogui.scroll(clicks)
            
            return {
                'success': True,
                'clicks': clicks,
                'position': (x, y) if x is not None and y is not None else 'current'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> Dict[str, Any]:
        """Drag from one position to another"""
        try:
            # Validate coordinates
            for x, y in [(start_x, start_y), (end_x, end_y)]:
                if not (0 <= x <= self.screen_width and 0 <= y <= self.screen_height):
                    return {
                        'success': False,
                        'error': f"Coordinates ({x}, {y}) are outside screen bounds"
                    }
            
            # Perform drag and drop
            pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
            
            return {
                'success': True,
                'start': (start_x, start_y),
                'end': (end_x, end_y),
                'duration': duration
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def open_application(self, app_name: str) -> Dict[str, Any]:
        """Open an application by name"""
        try:
            if self.platform == 'darwin':  # macOS
                subprocess.run(['open', '-a', app_name], check=True)
            elif self.platform == 'windows':
                subprocess.run(['start', app_name], shell=True, check=True)
            elif self.platform == 'linux':
                subprocess.run([app_name], check=True)
            else:
                return {
                    'success': False,
                    'error': f"Unsupported platform: {self.platform}"
                }
            
            # Wait for application to launch
            await asyncio.sleep(2)
            
            return {
                'success': True,
                'application': app_name,
                'platform': self.platform
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': f"Failed to open application: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_mouse_position(self) -> Dict[str, Any]:
        """Get current mouse position"""
        try:
            x, y = pyautogui.position()
            return {
                'success': True,
                'x': x,
                'y': y
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def move_mouse(self, x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
        """Move mouse to specific coordinates"""
        try:
            # Validate coordinates
            if not (0 <= x <= self.screen_width and 0 <= y <= self.screen_height):
                return {
                    'success': False,
                    'error': f"Coordinates ({x}, {y}) are outside screen bounds"
                }
            
            pyautogui.moveTo(x, y, duration=duration)
            
            return {
                'success': True,
                'coordinates': (x, y),
                'duration': duration
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def wait_for_image(self, image_path: str, timeout: int = 10, confidence: float = 0.8) -> Dict[str, Any]:
        """Wait for an image to appear on screen"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                if location is not None:
                    return {
                        'success': True,
                        'location': location,
                        'wait_time': time.time() - start_time
                    }
                await asyncio.sleep(0.5)
            
            return {
                'success': False,
                'error': f"Image not found within {timeout} seconds: {image_path}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_screen_info(self) -> Dict[str, Any]:
        """Get screen information"""
        try:
            return {
                'success': True,
                'width': self.screen_width,
                'height': self.screen_height,
                'platform': self.platform
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_image_template(self, x: int, y: int, width: int, height: int, filename: str) -> Dict[str, Any]:
        """Create an image template from a screen region for later matching"""
        try:
            # Take screenshot of the region
            region = (x, y, width, height)
            screenshot = pyautogui.screenshot(region=region)
            
            # Save the template
            template_path = os.path.join(self.screenshot_dir, f"template_{filename}.png")
            screenshot.save(template_path)
            
            return {
                'success': True,
                'template_path': template_path,
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }