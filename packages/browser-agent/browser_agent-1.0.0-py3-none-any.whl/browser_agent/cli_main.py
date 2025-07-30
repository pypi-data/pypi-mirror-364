
#!/usr/bin/env python3
"""
Professional CLI entry point for Browser Agent

This module provides the main entry point for the CLI application
with proper error handling, logging, and cross-platform support.
"""

import sys
import os
import argparse
import traceback
from pathlib import Path
from typing import Optional, List

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


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        prog="browser-agent",
        description=f"{APP_NAME} - AI-Powered Web Browser Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  browser-agent --gui                    # Launch GUI
    browser-agent --url https://example.com --task "Get page title"
    browser-agent --config                 # Show configuration
    browser-agent --setup                  # Run setup wizard
    browser-agent --version                # Show version
        """
    )
    
    # Main action arguments
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--gui", 
        action="store_true", 
        help="Launch the GUI application"
    )
    action_group.add_argument(
        "--setup", 
        action="store_true", 
        help="Run the setup wizard"
    )
    action_group.add_argument(
        "--config", 
        action="store_true", 
        help="Show current configuration"
    )
    action_group.add_argument(
        "--version", 
        action="store_true", 
        help="Show version information"
    )
    
    # Task execution arguments
    parser.add_argument(
        "--url", 
        type=str, 
        help="Target URL for automation task"
    )
    parser.add_argument(
        "--task", 
        type=str, 
        help="Task description for the AI agent"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output file for results (optional)"
    )
    
    # Configuration arguments
    parser.add_argument(
        "--browser", 
        choices=["chrome", "firefox", "edge", "safari"], 
        help="Browser to use for automation"
    )
    parser.add_argument(
        "--headless", 
        action="store_true", 
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--provider", 
        choices=["openai", "claude", "gemini"], 
        help="AI provider to use"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        help="AI model to use"
    )
    
    # Utility arguments
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose output"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode"
    )
    parser.add_argument(
        "--log-file", 
        type=str, 
        help="Custom log file path"
    )
    
    return parser


def show_version():
    """Show version information"""
    print(f"{APP_NAME} v{APP_VERSION}")
    print("AI-Powered Web Browser Automation")
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"Platform: {sys.platform}")


def show_config():
    """Show current configuration"""
    try:
        settings = settings_manager.settings
        
        print(f"📋 {APP_NAME} Configuration")
        print("=" * 40)
        
        print("\n🤖 AI Settings:")
        print(f"   Provider: {settings.ai_provider}")
        print(f"   Model: {settings.ai_model}")
        print(f"   Temperature: {settings.ai_temperature}")
        
        print("\n🌐 Browser Settings:")
        print(f"   Default Browser: {settings.default_browser}")
        print(f"   Headless Mode: {settings.headless_mode}")
        print(f"   Framework: {settings.automation_framework}")
        
        print("\n📁 Paths:")
        print(f"   Config Dir: {path_manager.config_dir}")
        print(f"   Data Dir: {path_manager.user_data_dir}")
        print(f"   Log File: {path_manager.log_file}")
        
        print("\n🔑 API Keys:")
        api_keys = {
            "OpenAI": bool(settings.openai_api_key),
            "Claude": bool(settings.claude_api_key),
            "Gemini": bool(settings.gemini_api_key)
        }
        for provider, configured in api_keys.items():
            status = "✅ Configured" if configured else "❌ Not configured"
            print(f"   {provider}: {status}")
            
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")


def run_setup():
    """Run the setup wizard"""
    print(f"🔧 {APP_NAME} Setup Wizard")
    print("=" * 40)
    
    try:
        # Import setup utilities
        from browser_agent.core.setup import SetupWizard
        
        wizard = SetupWizard()
        return wizard.run()
        
    except ImportError:
        print("❌ Setup wizard not available")
        print("   Please run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


def launch_gui():
    """Launch the GUI application"""
    try:
        from browser_agent.gui_main import main as gui_main
        return gui_main()
    except ImportError as e:
        print(f"❌ GUI not available: {e}")
        print("   Please install GUI dependencies: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        return 1


def execute_task(url: str, task: str, args) -> int:
    """Execute an automation task"""
    try:
        logger = get_logger(f"{APP_NAME}.cli")
        logger.info(f"Executing task: {task} on {url}")
        
        # Import core components
        from browser_agent.core.agent import BrowserAgent
        from browser_agent.core.multi_llm_processor import MultiLLMProcessor
        
        # Create agent with CLI configuration
        config_overrides = {}
        if args.browser:
            config_overrides['default_browser'] = args.browser
        if args.headless:
            config_overrides['headless_mode'] = True
        if args.provider:
            config_overrides['ai_provider'] = args.provider
        if args.model:
            config_overrides['ai_model'] = args.model
        
        # Initialize components
        llm_processor = MultiLLMProcessor()
        agent = BrowserAgent(llm_processor=llm_processor)
        
        # Execute the task
        print(f"🤖 Executing task: {task}")
        print(f"🌐 Target URL: {url}")
        
        result = agent.execute_task(url, task)
        
        # Handle output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(str(result), encoding='utf-8')
            print(f"📄 Results saved to: {output_path}")
        else:
            print("\n📋 Task Results:")
            print("=" * 40)
            print(result)
        
        logger.info("Task completed successfully")
        return 0
        
    except Exception as e:
        logger = get_logger(f"{APP_NAME}.cli")
        logger.error(f"Task execution failed: {e}")
        print(f"❌ Task execution failed: {e}")
        if args.debug:
            traceback.print_exc()
        return 1


def initialize_logging(args) -> bool:
    """Initialize logging system"""
    try:
        settings = settings_manager.settings
        
        log_level = "DEBUG" if args.debug else ("INFO" if args.verbose else settings.log_level)
        log_file = args.log_file if args.log_file else None
        
        setup_logging(
            log_level=log_level,
            log_to_file=settings.log_to_file,
            log_to_console=args.verbose or args.debug,
            log_file_path=log_file
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize logging: {e}")
        return False


def main() -> int:
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle version command early
    if args.version:
        show_version()
        return 0
    
    # Initialize logging
    if not initialize_logging(args):
        return 1
    
    logger = get_logger(f"{APP_NAME}.cli")
    
    try:
        logger.info(f"Starting {APP_NAME} CLI v{APP_VERSION}")
        
        # Handle different commands
        if args.gui:
            return launch_gui()
        
        elif args.setup:
            return 0 if run_setup() else 1
        
        elif args.config:
            show_config()
            return 0
        
        elif args.url and args.task:
            return execute_task(args.url, args.task, args)
        
        else:
            # No specific action, show help
            parser.print_help()
            return 0
            
    except KeyboardInterrupt:
        logger.info("CLI interrupted by user")
        print("\n👋 Interrupted by user")
        return 0
        
    except Exception as e:
        logger.error(f"CLI error: {e}")
        print(f"❌ Unexpected error: {e}")
        if args.debug:
            traceback.print_exc()
        return 1
        
    finally:
        try:
            shutdown_logging()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())