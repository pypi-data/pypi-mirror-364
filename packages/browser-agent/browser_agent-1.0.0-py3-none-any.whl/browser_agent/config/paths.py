"""Cross-platform path management for Browser Agent"""

import os
import sys
from pathlib import Path
from typing import Optional, Union
import platform
import appdirs


class PathManager:
    """Manages all file paths in a cross-platform way"""
    
    def __init__(self, app_name: str = "BrowserAgent", app_author: str = "BrowserAgentTeam"):
        self.app_name = app_name
        self.app_author = app_author
        self.system = platform.system().lower()
        
        # Get application directories using appdirs for cross-platform compatibility
        self._user_data_dir = Path(appdirs.user_data_dir(app_name, app_author))
        self._user_config_dir = Path(appdirs.user_config_dir(app_name, app_author))
        self._user_cache_dir = Path(appdirs.user_cache_dir(app_name, app_author))
        self._user_log_dir = Path(appdirs.user_log_dir(app_name, app_author))
        
        # Get package root directory
        self._package_root = Path(__file__).parent.parent
        self._project_root = self._package_root.parent
        
        # Initialize directories
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all necessary directories exist"""
        directories = [
            self._user_data_dir,
            self._user_config_dir,
            self._user_cache_dir,
            self._user_log_dir,
            self.screenshots_dir,
            self.exports_dir,
            self.plugins_dir,
            self.temp_dir,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def package_root(self) -> Path:
        """Get the package root directory"""
        return self._package_root
    
    @property
    def project_root(self) -> Path:
        """Get the project root directory"""
        return self._project_root
    
    @property
    def user_data_dir(self) -> Path:
        """Get user data directory"""
        return self._user_data_dir
    
    @property
    def user_config_dir(self) -> Path:
        """Get user config directory"""
        return self._user_config_dir
    
    @property
    def user_cache_dir(self) -> Path:
        """Get user cache directory"""
        return self._user_cache_dir
    
    @property
    def user_log_dir(self) -> Path:
        """Get user log directory"""
        return self._user_log_dir
    
    @property
    def screenshots_dir(self) -> Path:
        """Get screenshots directory"""
        return self._user_data_dir / "screenshots"
    
    @property
    def exports_dir(self) -> Path:
        """Get exports directory"""
        return self._user_data_dir / "exports"
    
    @property
    def plugins_dir(self) -> Path:
        """Get plugins directory"""
        return self._user_data_dir / "plugins"
    
    @property
    def temp_dir(self) -> Path:
        """Get temporary files directory"""
        return self._user_cache_dir / "temp"
    
    @property
    def assets_dir(self) -> Path:
        """Get assets directory"""
        return self._package_root / "assets"
    
    @property
    def gui_assets_dir(self) -> Path:
        """Get GUI assets directory"""
        return self._package_root / "gui" / "assets"
    
    @property
    def themes_dir(self) -> Path:
        """Get themes directory"""
        return self._package_root / "gui" / "themes"
    
    @property
    def config_file(self) -> Path:
        """Get main config file path"""
        return self._user_config_dir / "config.json"
    
    @property
    def settings_file(self) -> Path:
        """Get settings file path"""
        return self._user_config_dir / "settings.json"
    
    @property
    def task_history_file(self) -> Path:
        """Get task history file path"""
        return self._user_data_dir / "task_history.json"
    
    @property
    def mcp_servers_file(self) -> Path:
        """Get MCP servers config file path"""
        return self._user_config_dir / "mcp_servers.json"
    
    @property
    def log_file(self) -> Path:
        """Get main log file path"""
        return self._user_log_dir / "browser_agent.log"
    
    @property
    def env_file(self) -> Path:
        """Get environment file path (in project root for development)"""
        return self._project_root / ".env"
    
    def get_browser_profile_dir(self, browser: str) -> Path:
        """Get browser profile directory"""
        return self._user_data_dir / "browser_profiles" / browser
    
    def get_plugin_dir(self, plugin_name: str) -> Path:
        """Get specific plugin directory"""
        return self.plugins_dir / plugin_name
    
    def get_screenshot_path(self, filename: Optional[str] = None) -> Path:
        """Get screenshot file path"""
        if filename is None:
            import time
            filename = f"screenshot_{int(time.time())}.png"
        return self.screenshots_dir / filename
    
    def get_export_path(self, filename: str) -> Path:
        """Get export file path"""
        return self.exports_dir / filename
    
    def get_temp_path(self, filename: str) -> Path:
        """Get temporary file path"""
        return self.temp_dir / filename
    
    def resolve_path(self, path: Union[str, Path]) -> Path:
        """Resolve a path to absolute Path object"""
        path = Path(path)
        
        # If already absolute, return as-is
        if path.is_absolute():
            return path
        
        # Try relative to project root first
        project_path = self._project_root / path
        if project_path.exists():
            return project_path
        
        # Try relative to package root
        package_path = self._package_root / path
        if package_path.exists():
            return package_path
        
        # Try relative to user data dir
        user_path = self._user_data_dir / path
        if user_path.exists():
            return user_path
        
        # Default to project root
        return project_path
    
    def get_system_info(self) -> dict:
        """Get system information for debugging"""
        return {
            "system": self.system,
            "platform": platform.platform(),
            "python_version": sys.version,
            "package_root": str(self._package_root),
            "project_root": str(self._project_root),
            "user_data_dir": str(self._user_data_dir),
            "user_config_dir": str(self._user_config_dir),
            "user_cache_dir": str(self._user_cache_dir),
            "user_log_dir": str(self._user_log_dir),
        }
    
    def cleanup_temp_files(self, max_age_days: int = 7) -> None:
        """Clean up old temporary files"""
        import time
        
        if not self.temp_dir.exists():
            return
        
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        for file_path in self.temp_dir.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                    except OSError:
                        pass  # Ignore errors when deleting temp files


# Global path manager instance
path_manager = PathManager()