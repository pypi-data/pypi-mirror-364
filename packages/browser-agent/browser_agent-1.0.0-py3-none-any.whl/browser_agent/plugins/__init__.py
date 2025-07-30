"""Plugin system for extending browser agent capabilities"""

from .base import BasePlugin, PluginManager
from .registry import PluginRegistry

__all__ = ["BasePlugin", "PluginManager", "PluginRegistry"]