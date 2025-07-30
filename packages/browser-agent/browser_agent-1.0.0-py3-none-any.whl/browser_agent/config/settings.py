"""Settings management for Browser Agent"""

import json
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict, field
from copy import deepcopy

from .paths import path_manager
from .constants import DEFAULT_CONFIG, AI_PROVIDERS, SUPPORTED_BROWSERS

logger = logging.getLogger(__name__)


@dataclass
class Settings:
    """Application settings with validation and defaults"""
    
    # AI Configuration
    ai_provider: str = "openai"
    ai_model: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    max_tokens: int = 2000
    ai_timeout: int = 30
    
    # API Keys (stored separately for security)
    openai_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Browser Configuration
    default_browser: str = "chrome"
    automation_framework: str = "selenium"
    headless: bool = False
    window_width: int = 1920
    window_height: int = 1080
    page_load_timeout: int = 30
    implicit_wait: int = 10
    
    # GUI Configuration
    theme: str = "dark"
    color_theme: str = "blue"
    gui_width: int = 1400
    gui_height: int = 900
    font_size: int = 12
    
    # Behavior Settings
    screenshot_on_error: bool = True
    auto_scroll: bool = True
    human_like_delays: bool = True
    min_delay: float = 0.5
    max_delay: float = 2.0
    
    # Security Settings
    allow_file_downloads: bool = False
    allow_notifications: bool = False
    allow_location: bool = False
    sandbox_mode: bool = True
    
    # Logging Settings
    log_level: str = "INFO"
    log_to_file: bool = True
    max_log_size_mb: int = 10
    log_backup_count: int = 5
    
    # Performance Settings
    max_concurrent_browsers: int = 3
    screenshot_quality: int = 85
    cache_size_mb: int = 100
    memory_limit_mb: int = 1024
    
    # Plugin Settings
    plugins_enabled: bool = True
    auto_load_plugins: bool = True
    max_plugins: int = 20
    
    # MCP Settings
    mcp_enabled: bool = True
    mcp_auto_connect: bool = True
    max_mcp_servers: int = 10
    
    # Task Settings
    max_task_history: int = 1000
    auto_save_interval: int = 30
    task_timeout: int = 300
    
    # Desktop Automation
    desktop_automation_enabled: bool = True
    mouse_speed: float = 0.5
    keyboard_delay: float = 0.1
    
    # Advanced Settings
    debug_mode: bool = False
    experimental_features: bool = False
    telemetry_enabled: bool = False
    
    def validate(self) -> bool:
        """Validate settings values"""
        errors = []
        
        # Validate AI provider
        if self.ai_provider not in AI_PROVIDERS:
            errors.append(f"Invalid AI provider: {self.ai_provider}")
        
        # Validate AI model for provider
        if self.ai_provider in AI_PROVIDERS:
            provider_models = AI_PROVIDERS[self.ai_provider]["models"]
            if self.ai_model not in provider_models:
                errors.append(f"Invalid model {self.ai_model} for provider {self.ai_provider}")
        
        # Validate browser
        if self.default_browser not in SUPPORTED_BROWSERS:
            errors.append(f"Unsupported browser: {self.default_browser}")
        
        # Validate automation framework
        if self.automation_framework not in ["selenium", "playwright"]:
            errors.append(f"Invalid automation framework: {self.automation_framework}")
        
        # Validate numeric ranges
        if not 0 <= self.temperature <= 2:
            errors.append("Temperature must be between 0 and 2")
        
        if not 1 <= self.max_tokens <= 32000:
            errors.append("Max tokens must be between 1 and 32000")
        
        if not 800 <= self.window_width <= 3840:
            errors.append("Window width must be between 800 and 3840")
        
        if not 600 <= self.window_height <= 2160:
            errors.append("Window height must be between 600 and 2160")
        
        if not 1 <= self.page_load_timeout <= 300:
            errors.append("Page load timeout must be between 1 and 300 seconds")
        
        if not 0 <= self.min_delay <= self.max_delay <= 10:
            errors.append("Delays must be between 0 and 10 seconds, with min <= max")
        
        if not 1 <= self.max_concurrent_browsers <= 10:
            errors.append("Max concurrent browsers must be between 1 and 10")
        
        if not 10 <= self.screenshot_quality <= 100:
            errors.append("Screenshot quality must be between 10 and 100")
        
        if errors:
            logger.error(f"Settings validation failed: {'; '.join(errors)}")
            return False
        
        return True
    
    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """Get API key for the specified provider (or current provider)"""
        provider = provider or self.ai_provider
        
        if provider == "openai":
            return self.openai_api_key
        elif provider == "claude":
            return self.claude_api_key
        elif provider == "gemini":
            return self.gemini_api_key
        
        return None
    
    def set_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for the specified provider"""
        if provider == "openai":
            self.openai_api_key = api_key
        elif provider == "claude":
            self.claude_api_key = api_key
        elif provider == "gemini":
            self.gemini_api_key = api_key
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def has_api_key(self, provider: Optional[str] = None) -> bool:
        """Check if API key is configured for the provider"""
        api_key = self.get_api_key(provider)
        return api_key is not None and len(api_key.strip()) > 0
    
    def get_configured_providers(self) -> list:
        """Get list of providers with configured API keys"""
        providers = []
        for provider in AI_PROVIDERS.keys():
            if self.has_api_key(provider):
                providers.append(provider)
        return providers
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """Create settings from dictionary"""
        # Filter out unknown fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)


class SettingsManager:
    """Manages application settings with persistence"""
    
    def __init__(self):
        self.settings_file = path_manager.settings_file
        self._settings: Optional[Settings] = None
        self._callbacks = []
    
    @property
    def settings(self) -> Settings:
        """Get current settings, loading from file if necessary"""
        if self._settings is None:
            self._settings = self.load()
        return self._settings
    
    def load(self) -> Settings:
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                settings = Settings.from_dict(data)
                
                # Validate loaded settings
                if not settings.validate():
                    logger.warning("Loaded settings failed validation, using defaults")
                    settings = Settings()
                
                logger.info(f"Settings loaded from {self.settings_file}")
                return settings
            else:
                logger.info("No settings file found, using defaults")
                return Settings()
        
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            logger.info("Using default settings")
            return Settings()
    
    def save(self, settings: Optional[Settings] = None) -> bool:
        """Save settings to file"""
        if settings is None:
            settings = self.settings
        
        try:
            # Validate before saving
            if not settings.validate():
                logger.error("Cannot save invalid settings")
                return False
            
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)
            
            self._settings = settings
            logger.info(f"Settings saved to {self.settings_file}")
            
            # Notify callbacks
            self._notify_callbacks(settings)
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    
    def update(self, **kwargs) -> bool:
        """Update specific settings"""
        current = self.settings
        
        # Create new settings with updates
        data = current.to_dict()
        data.update(kwargs)
        
        new_settings = Settings.from_dict(data)
        
        return self.save(new_settings)
    
    def reset_to_defaults(self) -> bool:
        """Reset settings to defaults"""
        default_settings = Settings()
        return self.save(default_settings)
    
    def export_settings(self, file_path: Union[str, Path]) -> bool:
        """Export settings to a file"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings exported to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, file_path: Union[str, Path]) -> bool:
        """Import settings from a file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"Settings file not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            settings = Settings.from_dict(data)
            
            if not settings.validate():
                logger.error("Imported settings failed validation")
                return False
            
            return self.save(settings)
        
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False
    
    def add_change_callback(self, callback) -> None:
        """Add callback to be called when settings change"""
        self._callbacks.append(callback)
    
    def remove_change_callback(self, callback) -> None:
        """Remove settings change callback"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _notify_callbacks(self, settings: Settings) -> None:
        """Notify all callbacks of settings change"""
        for callback in self._callbacks:
            try:
                callback(settings)
            except Exception as e:
                logger.error(f"Settings callback error: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for debugging"""
        return {
            "settings_file": str(self.settings_file),
            "settings_file_exists": self.settings_file.exists(),
            "current_settings": self.settings.to_dict(),
            "configured_providers": self.settings.get_configured_providers(),
        }


# Global settings manager instance
settings_manager = SettingsManager()