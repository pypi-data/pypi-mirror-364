"""
Browser Agent - AI-powered web browser automation with GUI
"""

__version__ = "1.0.0"
__author__ = "Browser Agent Team"
__description__ = "AI-powered web automation with multi-LLM support and modern GUI"

from .core.agent import BrowserAgent
from .browsers.manager import BrowserManager
from .core.config import Config
from .core.multi_llm_processor import MultiLLMProcessor

# GUI components (optional import)
try:
    from .gui.main_window import MainWindow
    GUI_AVAILABLE = True
except ImportError:
    MainWindow = None
    GUI_AVAILABLE = False

__all__ = [
    "BrowserAgent", 
    "BrowserManager", 
    "Config", 
    "MultiLLMProcessor",
    "MainWindow",
    "GUI_AVAILABLE"
]