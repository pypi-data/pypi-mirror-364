#!/usr/bin/env python3
"""
Professional GUI entry point for Browser Agent

This module provides the main entry point for the GUI application
with proper error handling, logging, and cross-platform support.
"""

import sys
import os
import traceback
from pathlib import Path
from typing import Optional

# Add package to path if running as script
if __name__ == "__main__":
    package_root = Path(__file__).parent.parent
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))

try:
    from browser_agent.config.paths import path_manager
    from browser_agent.config.settings import settings_manager
    from browser_agent.config.constants import APP_NAME, APP_VERSION
    from browser_agent.utils.logging_config import setup_logging, get_logger, shutdown_logging
except ImportError as e:
    print(f"Failed to import Browser Agent modules: {e}")
    print("Please ensure the package is properly installed.")
    sys.exit(1)


def check_dependencies() -> bool:
    """Check if all required dependencies are available"""
    required_modules = [
        ('customtkinter', 'CustomTkinter GUI framework'),
        ('selenium', 'Selenium WebDriver'),
        ('requests', 'HTTP requests library'),
        ('PIL', 'Pillow image library'),
        ('dotenv', 'Python-dotenv'),
    ]
    
    missing = []
    for module, description in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append((module, description))
    
    if missing:
        print("❌ Missing required dependencies:")
        for module, description in missing:
            print(f"   - {module}: {description}")
        print("\nPlease install missing dependencies with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def check_python_version() -> bool:
    """Check if Python version is supported"""
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    return True


def initialize_application() -> bool:
    """Initialize the application environment"""
    try:
        # Setup logging first
        settings = settings_manager.settings
        setup_logging(
            log_level=settings.log_level,
            log_to_file=settings.log_to_file,
            log_to_console=True
        )
        
        logger = get_logger(f"{APP_NAME}.main")
        logger.info(f"Initializing {APP_NAME} v{APP_VERSION}")
        
        # Validate settings
        if not settings.validate():
            logger.warning("Settings validation failed, using defaults")
        
        # Clean up old files
        path_manager.cleanup_temp_files()
        
        logger.info("Application initialization complete")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        traceback.print_exc()
        return False


def launch_gui() -> int:
    """Launch the GUI application"""
    try:
        logger = get_logger(f"{APP_NAME}.gui")
        logger.info("Starting GUI application")
        
        # Import GUI components
        from browser_agent.gui.main_window import MainWindow
        
        # Create and run the main window
        app = MainWindow()
        logger.info("GUI application started successfully")
        
        # Run the application
        app.run()
        
        logger.info("GUI application closed normally")
        return 0
        
    except KeyboardInterrupt:
        logger = get_logger(f"{APP_NAME}.gui")
        logger.info("Application interrupted by user")
        return 0
        
    except Exception as e:
        logger = get_logger(f"{APP_NAME}.gui")
        logger.error(f"GUI application error: {e}")
        logger.error(traceback.format_exc())
        
        # Show error dialog if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            
            messagebox.showerror(
                "Browser Agent Error",
                f"An error occurred while running the application:\n\n{str(e)}\n\n"
                f"Please check the log file for more details:\n{path_manager.log_file}"
            )
            
            root.destroy()
            
        except Exception:
            pass  # If we can't show the dialog, just continue
        
        return 1


def main() -> int:
    """Main entry point for the GUI application"""
    try:
        # Print banner
        print(f"🤖 {APP_NAME} v{APP_VERSION}")
        print("AI-Powered Web Browser Automation")
        print("=" * 40)
        
        # Check system requirements
        if not check_python_version():
            return 1
        
        if not check_dependencies():
            return 1
        
        # Initialize application
        if not initialize_application():
            return 1
        
        # Launch GUI
        return launch_gui()
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return 1
        
    finally:
        # Cleanup
        try:
            shutdown_logging()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())