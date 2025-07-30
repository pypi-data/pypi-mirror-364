#!/usr/bin/env python3
"""
Command Line Interface for Browser Agent
"""

import argparse
import asyncio
import json
import sys
from typing import Dict, Any
from pathlib import Path

from .core.agent import BrowserAgent
from .core.config import Config
from .browsers.detector import BrowserDetector
from .utils.scheduler import TaskScheduler, ScheduledTask, TaskStatus


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        try:
            asyncio.run(args.func(args))
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="Browser Agent - AI-powered web automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  browser-agent run "Search for Python tutorials on YouTube"
    browser-agent run "Book a flight from NYC to LA" --browser firefox
    browser-agent detect-browsers
    browser-agent schedule "Check my email" --daily "09:00"
        """
    )
    
    # Global options
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--browser', type=str, default='chrome', 
                       help='Browser to use (chrome, firefox, edge, safari)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Execute a browser automation task')
    run_parser.add_argument('prompt', type=str, help='Task description prompt')
    run_parser.add_argument('--output', type=str, help='Output file for results')
    run_parser.add_argument('--screenshot', action='store_true', help='Take screenshots')
    run_parser.set_defaults(func=run_task)
    
    # Detect browsers command
    detect_parser = subparsers.add_parser('detect-browsers', help='Detect available browsers')
    detect_parser.set_defaults(func=detect_browsers)
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule a task')
    schedule_parser.add_argument('prompt', type=str, help='Task description prompt')
    schedule_parser.add_argument('--daily', type=str, metavar='TIME', help='Run daily at TIME (HH:MM)')
    schedule_parser.add_argument('--weekly', type=str, metavar='DAY:TIME', help='Run weekly on DAY at TIME')
    schedule_parser.add_argument('--interval', type=str, metavar='INTERVAL', help='Run every INTERVAL (e.g., 30m, 2h)')
    schedule_parser.add_argument('--once', type=str, metavar='DATETIME', help='Run once at DATETIME')
    schedule_parser.add_argument('--name', type=str, help='Task name')
    schedule_parser.set_defaults(func=schedule_task)
    
    # List tasks command
    list_parser = subparsers.add_parser('list-tasks', help='List scheduled tasks')
    list_parser.set_defaults(func=list_tasks)
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive mode')
    interactive_parser.set_defaults(func=interactive_mode)
    
    return parser


async def run_task(args) -> None:
    """Execute a browser automation task"""
    config = load_config(args)
    
    if args.verbose:
        config.log_level = "DEBUG"
    
    if args.headless:
        config.headless = True
    
    if args.screenshot:
        config.screenshot_on_error = True
    
    print(f"🤖 Starting browser agent with {args.browser}")
    print(f"📝 Task: {args.prompt}")
    
    async with BrowserAgent(config) as agent:
        result = await agent.execute_task(args.prompt, args.browser)
        
        # Display results
        print(f"\n✅ Task completed in {result.execution_time:.2f} seconds")
        print(f"🎯 Success: {result.success}")
        
        if result.error_message:
            print(f"❌ Error: {result.error_message}")
        
        if result.screenshots:
            print(f"📸 Screenshots saved: {len(result.screenshots)}")
            for screenshot in result.screenshots:
                print(f"   - {screenshot}")
        
        # Save results if output file specified
        if args.output:
            save_results(result, args.output)
            print(f"💾 Results saved to {args.output}")


async def detect_browsers(args) -> None:
    """Detect available browsers"""
    print("🔍 Detecting available browsers...")
    
    detector = BrowserDetector()
    browsers = detector.detect_all()
    
    if not browsers:
        print("❌ No browsers detected")
        return
    
    print(f"\n✅ Found {len(browsers)} browser(s):")
    
    for name, info in browsers.items():
        status = "✅" if info.is_installed else "❌"
        version = f" (v{info.version})" if info.version else ""
        print(f"   {status} {info.name}{version}")
        if info.is_installed:
            print(f"      Path: {info.executable_path}")
    
    # Check running browsers
    running = detector.get_running_browsers()
    if running:
        print(f"\n🏃 Currently running: {', '.join(running)}")


async def schedule_task(args) -> None:
    """Schedule a task for later execution"""
    config = load_config(args)
    
    # Determine schedule type and time
    if args.daily:
        schedule_type = "daily"
        schedule_time = args.daily
    elif args.weekly:
        schedule_type = "weekly"
        schedule_time = args.weekly
    elif args.interval:
        schedule_type = "interval"
        schedule_time = args.interval
    elif args.once:
        schedule_type = "once"
        schedule_time = args.once
    else:
        print("❌ Please specify a schedule option (--daily, --weekly, --interval, or --once)")
        return
    
    # Create scheduled task
    task_name = args.name or f"Task_{int(time.time())}"
    task_id = task_name.lower().replace(" ", "_")
    
    task = ScheduledTask(
        id=task_id,
        name=task_name,
        prompt=args.prompt,
        browser=args.browser,
        schedule_type=schedule_type,
        schedule_time=schedule_time
    )
    
    # Create agent and scheduler
    agent = BrowserAgent(config)
    scheduler = TaskScheduler(agent)
    
    # Add task
    if scheduler.add_task(task):
        print(f"✅ Task '{task_name}' scheduled successfully")
        print(f"📅 Schedule: {schedule_type} at {schedule_time}")
        print(f"🎯 Next run: {task.next_run}")
        
        # Start scheduler
        scheduler.start_scheduler()
        print("\n🔄 Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop_scheduler()
            print("\n⏹️ Scheduler stopped")
    else:
        print("❌ Failed to schedule task")


async def list_tasks(args) -> None:
    """List scheduled tasks"""
    # This would typically load from a persistent store
    print("📋 Scheduled Tasks:")
    print("   (No persistent storage implemented yet)")


async def interactive_mode(args) -> None:
    """Start interactive mode"""
    config = load_config(args)
    
    print("🤖 Browser Agent - Interactive Mode")
    print("Type 'help' for commands, 'quit' to exit")
    
    agent = BrowserAgent(config)
    
    try:
        while True:
            try:
                prompt = input("\n> ").strip()
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    break
                elif prompt.lower() == 'help':
                    print_help()
                elif prompt.lower() == 'browsers':
                    await detect_browsers(args)
                elif prompt.lower().startswith('browser '):
                    browser = prompt.split(' ', 1)[1]
                    agent.switch_browser(browser)
                    print(f"Switched to {browser}")
                elif prompt:
                    result = await agent.execute_task(prompt, args.browser)
                    print(f"✅ Task completed: {result.success}")
                    if result.error_message:
                        print(f"❌ Error: {result.error_message}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    finally:
        agent.close()
        print("\n👋 Goodbye!")


def print_help():
    """Print interactive mode help"""
    help_text = """
Available commands:
  help          - Show this help
  browsers      - List available browsers  
  browser <name>- Switch to browser
  quit/exit/q   - Exit interactive mode
  
Or just type a task description to execute it.
    """
    print(help_text)


def load_config(args) -> Config:
    """Load configuration from file or create default"""
    if args.config and Path(args.config).exists():
        with open(args.config) as f:
            config_data = json.load(f)
        return Config.from_dict(config_data)
    else:
        return Config()


def save_results(result, output_file: str):
    """Save execution results to file"""
    result_data = {
        'success': result.success,
        'execution_time': result.execution_time,
        'error_message': result.error_message,
        'step_results': result.step_results,
        'screenshots': result.screenshots
    }
    
    with open(output_file, 'w') as f:
        json.dump(result_data, f, indent=2, default=str)


if __name__ == '__main__':
    main()