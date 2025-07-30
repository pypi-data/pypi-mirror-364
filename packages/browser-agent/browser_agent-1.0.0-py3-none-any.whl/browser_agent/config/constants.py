"""Application constants for Browser Agent"""

# Application Information
APP_NAME = "Browser Agent"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Browser Agent Team"
APP_DESCRIPTION = "AI-powered web browser automation with multi-LLM support"
APP_URL = "https://github.com/AryanVBW/browser-agent"

# Supported Python Versions
MIN_PYTHON_VERSION = (3, 8)
RECOMMENDED_PYTHON_VERSION = (3, 12)

# Supported Browsers
SUPPORTED_BROWSERS = {
    "chrome": "Google Chrome",
    "firefox": "Mozilla Firefox", 
    "edge": "Microsoft Edge",
    "safari": "Safari",
    "opera": "Opera",
}

# Default Browser Configurations
DEFAULT_BROWSER_CONFIG = {
    "headless": False,
    "window_size": (1920, 1080),
    "page_load_timeout": 30,
    "implicit_wait": 10,
    "user_agent": None,  # Use browser default
}

# Automation Frameworks
AUTOMATION_FRAMEWORKS = {
    "selenium": "Selenium WebDriver",
    "playwright": "Microsoft Playwright",
}

# AI Providers and Models
AI_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": {
            "gpt-3.5-turbo": "GPT-3.5 Turbo",
            "gpt-3.5-turbo-16k": "GPT-3.5 Turbo 16K",
            "gpt-4": "GPT-4",
            "gpt-4-turbo": "GPT-4 Turbo",
            "gpt-4o": "GPT-4o",
        },
        "default_model": "gpt-3.5-turbo",
        "api_key_env": "OPENAI_API_KEY",
    },
    "claude": {
        "name": "Anthropic Claude",
        "models": {
            "claude-3-haiku-20240307": "Claude 3 Haiku",
            "claude-3-sonnet-20240229": "Claude 3 Sonnet",
            "claude-3-opus-20240229": "Claude 3 Opus",
        },
        "default_model": "claude-3-sonnet-20240229",
        "api_key_env": "CLAUDE_API_KEY",
    },
    "gemini": {
        "name": "Google Gemini",
        "models": {
            "gemini-pro": "Gemini Pro",
            "gemini-pro-vision": "Gemini Pro Vision",
        },
        "default_model": "gemini-pro",
        "api_key_env": "GEMINI_API_KEY",
    },
}

# Default AI Configuration
DEFAULT_AI_CONFIG = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.1,
    "max_tokens": 2000,
    "timeout": 30,
}

# GUI Configuration
GUI_CONFIG = {
    "theme": "dark",
    "color_theme": "blue",
    "window_size": (1400, 900),
    "min_window_size": (1200, 700),
    "font_family": "Segoe UI",
    "font_sizes": {
        "small": 10,
        "normal": 12,
        "large": 14,
        "title": 18,
        "header": 24,
    },
}

# Color Schemes
COLOR_SCHEMES = {
    "dark": {
        "primary": "#1f538d",
        "secondary": "#2d5aa0",
        "accent": "#36719f",
        "success": "#2fa572",
        "warning": "#ff8800",
        "error": "#e74c3c",
        "text": "#ffffff",
        "text_secondary": "#888888",
        "bg_primary": "#212121",
        "bg_secondary": "#2d2d2d",
        "bg_tertiary": "#3d3d3d",
    },
    "light": {
        "primary": "#1f538d",
        "secondary": "#2d5aa0",
        "accent": "#36719f",
        "success": "#2fa572",
        "warning": "#ff8800",
        "error": "#e74c3c",
        "text": "#000000",
        "text_secondary": "#666666",
        "bg_primary": "#ffffff",
        "bg_secondary": "#f5f5f5",
        "bg_tertiary": "#e0e0e0",
    },
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
}

# Security Settings
SECURITY_CONFIG = {
    "allow_file_downloads": False,
    "allow_notifications": False,
    "allow_location": False,
    "allow_microphone": False,
    "allow_camera": False,
    "sandbox_mode": True,
    "disable_web_security": False,
}

# Performance Settings
PERFORMANCE_CONFIG = {
    "max_concurrent_browsers": 3,
    "screenshot_quality": 85,
    "screenshot_format": "PNG",
    "cache_size_mb": 100,
    "memory_limit_mb": 1024,
}

# Network Settings
NETWORK_CONFIG = {
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1,
    "user_agent": f"{APP_NAME}/{APP_VERSION}",
}

# File Extensions
FILE_EXTENSIONS = {
    "screenshots": [".png", ".jpg", ".jpeg"],
    "exports": [".json", ".csv", ".xlsx", ".pdf"],
    "configs": [".json", ".yaml", ".yml"],
    "logs": [".log", ".txt"],
    "plugins": [".py"],
}

# MCP (Model Context Protocol) Settings
MCP_CONFIG = {
    "default_timeout": 30,
    "max_servers": 10,
    "auto_connect": True,
    "marketplace_url": "https://github.com/modelcontextprotocol/servers",
}

# Plugin System
PLUGIN_CONFIG = {
    "auto_load": True,
    "max_plugins": 20,
    "plugin_timeout": 60,
    "builtin_plugins_dir": "plugins/builtin",
    "user_plugins_dir": "plugins/user",
}

# Task Management
TASK_CONFIG = {
    "max_history_items": 1000,
    "auto_save_interval": 30,  # seconds
    "task_timeout": 300,  # 5 minutes
    "max_retries": 3,
}

# Desktop Automation
DESKTOP_CONFIG = {
    "screenshot_interval": 1,  # seconds
    "mouse_speed": 0.5,
    "keyboard_delay": 0.1,
    "confidence_threshold": 0.8,
}

# Error Messages
ERROR_MESSAGES = {
    "no_api_key": "No API key configured for the selected AI provider. Please add your API key in the Brain/LLM tab.",
    "browser_not_found": "No supported browser found. Please install Chrome, Firefox, or Edge.",
    "connection_failed": "Failed to connect to the AI service. Please check your internet connection and API key.",
    "automation_failed": "Browser automation failed. Please check the browser status and try again.",
    "plugin_error": "Plugin execution failed. Please check the plugin configuration.",
    "file_not_found": "The specified file was not found.",
    "permission_denied": "Permission denied. Please check file permissions.",
    "invalid_config": "Invalid configuration. Please check your settings.",
}

# Success Messages
SUCCESS_MESSAGES = {
    "task_completed": "Task completed successfully!",
    "browser_connected": "Browser connected successfully.",
    "ai_connected": "AI service connected successfully.",
    "plugin_loaded": "Plugin loaded successfully.",
    "config_saved": "Configuration saved successfully.",
    "export_completed": "Export completed successfully.",
}

# Default Configurations
DEFAULT_CONFIG = {
    "app": {
        "name": APP_NAME,
        "version": APP_VERSION,
        "first_run": True,
    },
    "ai": DEFAULT_AI_CONFIG,
    "browser": DEFAULT_BROWSER_CONFIG,
    "gui": GUI_CONFIG,
    "logging": LOGGING_CONFIG,
    "security": SECURITY_CONFIG,
    "performance": PERFORMANCE_CONFIG,
    "network": NETWORK_CONFIG,
    "mcp": MCP_CONFIG,
    "plugins": PLUGIN_CONFIG,
    "tasks": TASK_CONFIG,
    "desktop": DESKTOP_CONFIG,
}