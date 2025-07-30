import importlib
import os
import sys
from typing import Dict, List, Type
from .base import BasePlugin, PluginMetadata


class PluginRegistry:
    """Registry for discovering and loading plugins"""
    
    def __init__(self, plugin_directories: List[str] = None):
        self.plugin_directories = plugin_directories or []
        self.discovered_plugins = {}
        self.loaded_plugins = {}
    
    def add_plugin_directory(self, directory: str):
        """Add a directory to search for plugins"""
        if os.path.exists(directory):
            self.plugin_directories.append(directory)
    
    def discover_plugins(self) -> Dict[str, str]:
        """Discover all available plugins in the configured directories"""
        discovered = {}
        
        # Discover built-in plugins
        builtin_plugins = self._discover_builtin_plugins()
        discovered.update(builtin_plugins)
        
        # Discover plugins in external directories
        for directory in self.plugin_directories:
            external_plugins = self._discover_external_plugins(directory)
            discovered.update(external_plugins)
        
        self.discovered_plugins = discovered
        return discovered
    
    def _discover_builtin_plugins(self) -> Dict[str, str]:
        """Discover built-in plugins"""
        plugins = {}
        
        # Define built-in plugins
        builtin_plugin_modules = [
            'form_filler',
            'ecommerce',
            'social_media',
            'data_extractor',
            'booking',
        ]
        
        for module_name in builtin_plugin_modules:
            try:
                module_path = f"browser_agent.plugins.builtin.{module_name}"
                plugins[module_name] = module_path
            except Exception:
                continue
        
        return plugins
    
    def _discover_external_plugins(self, directory: str) -> Dict[str, str]:
        """Discover plugins in an external directory"""
        plugins = {}
        
        if not os.path.exists(directory):
            return plugins
        
        # Add directory to Python path temporarily
        original_path = sys.path.copy()
        if directory not in sys.path:
            sys.path.insert(0, directory)
        
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                
                # Check for Python files
                if item.endswith('.py') and not item.startswith('_'):
                    plugin_name = item[:-3]  # Remove .py extension
                    plugins[plugin_name] = item_path
                
                # Check for Python packages
                elif os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, '__init__.py')):
                    plugins[item] = item_path
        
        finally:
            # Restore original Python path
            sys.path = original_path
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> BasePlugin:
        """Load a specific plugin by name"""
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]
        
        if plugin_name not in self.discovered_plugins:
            raise ValueError(f"Plugin {plugin_name} not found. Run discover_plugins() first.")
        
        plugin_path = self.discovered_plugins[plugin_name]
        
        try:
            # Import the plugin module
            if plugin_path.startswith('browser_agent.plugins'):
                # Built-in plugin
                module = importlib.import_module(plugin_path)
            else:
                # External plugin
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            
            # Find the plugin class
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                raise ValueError(f"No plugin class found in {plugin_name}")
            
            # Instantiate the plugin
            plugin_instance = plugin_class()
            self.loaded_plugins[plugin_name] = plugin_instance
            
            return plugin_instance
            
        except Exception as e:
            raise RuntimeError(f"Failed to load plugin {plugin_name}: {e}")
    
    def _find_plugin_class(self, module) -> Type[BasePlugin]:
        """Find the plugin class in a module"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, BasePlugin) and 
                attr != BasePlugin):
                return attr
        return None
    
    def load_all_plugins(self) -> Dict[str, BasePlugin]:
        """Load all discovered plugins"""
        loaded = {}
        
        for plugin_name in self.discovered_plugins:
            try:
                plugin = self.load_plugin(plugin_name)
                loaded[plugin_name] = plugin
            except Exception as e:
                print(f"Failed to load plugin {plugin_name}: {e}")
        
        return loaded
    
    def get_plugin_info(self, plugin_name: str) -> Dict:
        """Get information about a plugin without loading it"""
        if plugin_name not in self.discovered_plugins:
            return {}
        
        info = {
            'name': plugin_name,
            'path': self.discovered_plugins[plugin_name],
            'loaded': plugin_name in self.loaded_plugins
        }
        
        # If plugin is loaded, include metadata
        if plugin_name in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_name]
            info['metadata'] = plugin.metadata
        
        return info
    
    def list_all_plugins(self) -> Dict[str, Dict]:
        """List all discovered plugins with their information"""
        return {
            name: self.get_plugin_info(name)
            for name in self.discovered_plugins
        }