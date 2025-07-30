"""Configuration management for Browser Agent

This module provides backward compatibility with the old Config class
while using the new professional configuration system.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

from ..config.settings import settings_manager, Settings
from ..config.paths import path_manager
from ..config.constants import AI_PROVIDERS, DEFAULT_CONFIG

# Load environment variables
load_dotenv(path_manager.env_file)

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Legacy configuration class for backward compatibility
    
    This class provides backward compatibility with existing code
    while delegating to the new settings system.
    """
    
    def __init__(self):
        """Initialize config from settings manager"""
        self._settings = settings_manager.settings
        self._load_env_vars()
    
    def _load_env_vars(self):
        """Load API keys from environment variables if not in settings"""
        # Load API keys from environment if not already configured
        for provider, config in AI_PROVIDERS.items():
            env_key = config["api_key_env"]
            env_value = os.getenv(env_key)
            
            if env_value and not self._settings.has_api_key(provider):
                self._settings.set_api_key(provider, env_value)
                logger.info(f"Loaded {provider} API key from environment")
    
    # AI Settings
    @property
    def openai_api_key(self) -> Optional[str]:
        return self._settings.openai_api_key or os.getenv("OPENAI_API_KEY")
    
    @property
    def claude_api_key(self) -> Optional[str]:
        return self._settings.claude_api_key or os.getenv("CLAUDE_API_KEY")
    
    @property
    def gemini_api_key(self) -> Optional[str]:
        return self._settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    
    @property
    def ai_model(self) -> str:
        return self._settings.ai_model
    
    @property
    def ai_provider(self) -> str:
        return self._settings.ai_provider
    
    @property
    def max_tokens(self) -> int:
        return self._settings.max_tokens
    
    @property
    def temperature(self) -> float:
        return self._settings.temperature
    
    # Browser Settings
    @property
    def default_browser(self) -> str:
        return self._settings.default_browser
    
    @property
    def headless(self) -> bool:
        return self._settings.headless
    
    @property
    def automation_framework(self) -> str:
        return self._settings.automation_framework
    
    @property
    def page_load_timeout(self) -> int:
        return self._settings.page_load_timeout
    
    @property
    def implicit_wait(self) -> int:
        return self._settings.implicit_wait
    
    # Window Settings
    @property
    def window_width(self) -> int:
        return self._settings.window_width
    
    @property
    def window_height(self) -> int:
        return self._settings.window_height
    
    # Behavior Settings
    @property
    def screenshot_on_error(self) -> bool:
        return self._settings.screenshot_on_error
    
    @property
    def auto_scroll(self) -> bool:
        return self._settings.auto_scroll
    
    @property
    def human_like_delays(self) -> bool:
        return self._settings.human_like_delays
    
    @property
    def min_delay(self) -> float:
        return self._settings.min_delay
    
    @property
    def max_delay(self) -> float:
        return self._settings.max_delay
    
    # Security Settings
    @property
    def allow_file_downloads(self) -> bool:
        return self._settings.allow_file_downloads
    
    @property
    def allow_notifications(self) -> bool:
        return self._settings.allow_notifications
    
    @property
    def allow_location(self) -> bool:
        return self._settings.allow_location
    
    @property
    def allow_microphone(self) -> bool:
        return False  # Always false for security
    
    @property
    def allow_camera(self) -> bool:
        return False  # Always false for security
    
    # Logging Settings
    @property
    def log_level(self) -> str:
        return self._settings.log_level
    
    @property
    def log_file(self) -> Optional[str]:
        return str(path_manager.log_file) if self._settings.log_to_file else None
    
    # Plugin Settings
    @property
    def plugins_enabled(self) -> bool:
        return self._settings.plugins_enabled
    
    @property
    def plugin_directory(self) -> str:
        return str(path_manager.plugins_dir)
    
    # Container Settings (deprecated)
    @property
    def use_container(self) -> bool:
        return False  # Deprecated feature
    
    @property
    def container_image(self) -> str:
        return "selenium/standalone-chrome:latest"  # Deprecated
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        return self._settings.validate()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create config from dictionary"""
        # Update settings from dictionary
        settings_manager.update(**config_dict)
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "openai_api_key": self.openai_api_key,
            "claude_api_key": self.claude_api_key,
            "gemini_api_key": self.gemini_api_key,
            "ai_model": self.ai_model,
            "ai_provider": self.ai_provider,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "default_browser": self.default_browser,
            "headless": self.headless,
            "automation_framework": self.automation_framework,
            "page_load_timeout": self.page_load_timeout,
            "implicit_wait": self.implicit_wait,
            "window_width": self.window_width,
            "window_height": self.window_height,
            "screenshot_on_error": self.screenshot_on_error,
            "auto_scroll": self.auto_scroll,
            "human_like_delays": self.human_like_delays,
            "min_delay": self.min_delay,
            "max_delay": self.max_delay,
            "allow_file_downloads": self.allow_file_downloads,
            "allow_notifications": self.allow_notifications,
            "allow_location": self.allow_location,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "plugins_enabled": self.plugins_enabled,
            "plugin_directory": self.plugin_directory,
        }