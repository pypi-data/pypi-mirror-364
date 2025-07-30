import abc
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class PluginMetadata:
    """Metadata for a plugin"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = None
    supported_browsers: List[str] = None
    category: str = "general"


class BasePlugin(abc.ABC):
    """Base class for all browser agent plugins"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")
        self.enabled = True
        self._agent = None
        self._automation = None
    
    @property
    @abc.abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass
    
    def initialize(self, agent, automation) -> bool:
        """Initialize the plugin with agent and automation instances"""
        try:
            self._agent = agent
            self._automation = automation
            return self.on_initialize()
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin: {e}")
            return False
    
    def on_initialize(self) -> bool:
        """Override this method for custom initialization logic"""
        return True
    
    def on_shutdown(self):
        """Override this method for cleanup logic"""
        pass
    
    @abc.abstractmethod
    def can_handle(self, task_type: str, context: Dict[str, Any]) -> bool:
        """Check if this plugin can handle the given task"""
        pass
    
    @abc.abstractmethod
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plugin's main functionality"""
        pass
    
    def get_supported_actions(self) -> List[str]:
        """Return list of actions this plugin supports"""
        return []
    
    def validate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Validate task data before execution"""
        return True


class PluginManager:
    """Manages plugin loading, initialization, and execution"""
    
    def __init__(self, agent=None):
        self.agent = agent
        self.plugins = {}
        self.enabled_plugins = set()
        self.logger = logging.getLogger(__name__)
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Register a plugin"""
        try:
            if not isinstance(plugin, BasePlugin):
                raise ValueError("Plugin must inherit from BasePlugin")
            
            metadata = plugin.metadata
            plugin_name = metadata.name
            
            # Check for conflicts
            if plugin_name in self.plugins:
                self.logger.warning(f"Plugin {plugin_name} already registered, replacing")
            
            # Initialize plugin if agent is available
            if self.agent and hasattr(self.agent, 'automation'):
                if plugin.initialize(self.agent, self.agent.automation):
                    self.plugins[plugin_name] = plugin
                    self.enabled_plugins.add(plugin_name)
                    self.logger.info(f"Plugin {plugin_name} registered and initialized")
                    return True
                else:
                    self.logger.error(f"Plugin {plugin_name} initialization failed")
                    return False
            else:
                # Store plugin for later initialization
                self.plugins[plugin_name] = plugin
                self.logger.info(f"Plugin {plugin_name} registered (pending initialization)")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to register plugin: {e}")
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin"""
        try:
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                plugin.on_shutdown()
                del self.plugins[plugin_name]
                self.enabled_plugins.discard(plugin_name)
                self.logger.info(f"Plugin {plugin_name} unregistered")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to unregister plugin {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a registered plugin"""
        if plugin_name in self.plugins:
            self.enabled_plugins.add(plugin_name)
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        self.enabled_plugins.discard(plugin_name)
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a specific plugin"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all registered plugins with their metadata"""
        result = {}
        for name, plugin in self.plugins.items():
            result[name] = {
                'metadata': plugin.metadata,
                'enabled': name in self.enabled_plugins,
                'initialized': plugin._agent is not None
            }
        return result
    
    def find_capable_plugins(self, task_type: str, context: Dict[str, Any]) -> List[BasePlugin]:
        """Find plugins that can handle a specific task"""
        capable_plugins = []
        
        for plugin_name, plugin in self.plugins.items():
            if plugin_name in self.enabled_plugins:
                try:
                    if plugin.can_handle(task_type, context):
                        capable_plugins.append(plugin)
                except Exception as e:
                    self.logger.error(f"Error checking plugin {plugin_name} capability: {e}")
        
        return capable_plugins
    
    async def execute_with_plugin(self, plugin_name: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using a specific plugin"""
        if plugin_name not in self.plugins:
            return {
                'success': False,
                'error': f"Plugin {plugin_name} not found"
            }
        
        if plugin_name not in self.enabled_plugins:
            return {
                'success': False,
                'error': f"Plugin {plugin_name} is disabled"
            }
        
        plugin = self.plugins[plugin_name]
        
        try:
            # Validate task data
            if not plugin.validate_task_data(task_data):
                return {
                    'success': False,
                    'error': f"Invalid task data for plugin {plugin_name}"
                }
            
            # Execute plugin
            result = await plugin.execute(task_data)
            
            # Ensure result has required fields
            if not isinstance(result, dict):
                result = {'success': True, 'result': result}
            
            if 'success' not in result:
                result['success'] = True
            
            return result
            
        except Exception as e:
            self.logger.error(f"Plugin {plugin_name} execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'plugin': plugin_name
            }
    
    def initialize_all_plugins(self, agent, automation):
        """Initialize all registered plugins"""
        self.agent = agent
        
        for plugin_name, plugin in self.plugins.items():
            try:
                if plugin.initialize(agent, automation):
                    self.enabled_plugins.add(plugin_name)
                    self.logger.info(f"Plugin {plugin_name} initialized")
                else:
                    self.logger.warning(f"Plugin {plugin_name} initialization failed")
            except Exception as e:
                self.logger.error(f"Error initializing plugin {plugin_name}: {e}")
    
    def shutdown_all_plugins(self):
        """Shutdown all plugins"""
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.on_shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down plugin {plugin_name}: {e}")
        
        self.enabled_plugins.clear()