import logging
import time
import threading
from typing import Dict, Optional, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import playwright
from playwright.sync_api import sync_playwright

from .detector import BrowserDetector, BrowserInfo
from .support import get_browser_support_manager, BrowserSupport


class BrowserManager:
    """Manages browser instances and automation frameworks with enhanced error handling"""
    
    def __init__(self, headless: bool = False, framework: str = "selenium"):
        self.headless = headless
        self.framework = framework.lower()
        self.detector = BrowserDetector()
        self.support_manager = get_browser_support_manager()
        self.available_browsers = self.detector.detect_all()
        self.active_driver = None
        self.playwright_context = None
        self.logger = logging.getLogger(__name__)
        self.session_lock = threading.Lock()
        self.last_activity = time.time()
        self.session_timeout = 300  # 5 minutes
        
        # Validate available browsers
        self._validate_browser_support()
    
    def _validate_browser_support(self):
        """Validate and filter browsers based on support matrix"""
        validated_browsers = {}
        
        for name, browser_info in self.available_browsers.items():
            # Check if browser is supported
            compatibility = self.support_manager.check_browser_compatibility(name)
            
            if compatibility['supported'] and browser_info.is_installed:
                validated_browsers[name] = browser_info
                self.logger.info(f"✅ {browser_info.name} - {compatibility['support_level']}")
                
                # Log warnings for partially supported browsers
                if 'warnings' in compatibility:
                    for warning in compatibility['warnings']:
                        self.logger.warning(f"⚠️ {browser_info.name}: {warning}")
            else:
                self.logger.warning(f"❌ {name} - Not supported or not installed")
        
        self.available_browsers = validated_browsers
        
        # Log recommendations if no browsers available
        if not self.available_browsers:
            missing = ['chrome', 'firefox', 'edge']
            recommendations = self.support_manager.generate_setup_recommendations(missing)
            self.logger.error("No supported browsers found!")
            self.logger.info(f"\n{recommendations}")
    
    def is_session_active(self) -> bool:
        """Check if browser session is active and responsive"""
        if not self.active_driver:
            return False
        
        try:
            with self.session_lock:
                if self.framework == "selenium":
                    # Try to get current URL to test session
                    _ = self.active_driver.current_url
                    self.last_activity = time.time()
                    return True
                elif self.framework == "playwright":
                    if isinstance(self.active_driver, dict) and 'page' in self.active_driver:
                        # Check if page is still active
                        _ = self.active_driver['page'].url
                        self.last_activity = time.time()
                        return True
        except Exception as e:
            self.logger.warning(f"Browser session check failed: {e}")
            return False
        
        return False
    
    def check_session_timeout(self) -> bool:
        """Check if session has timed out"""
        if time.time() - self.last_activity > self.session_timeout:
            self.logger.warning("Browser session timed out")
            return True
        return False
        
    def get_available_browsers(self) -> Dict[str, BrowserInfo]:
        """Get all available browsers on the system"""
        return self.available_browsers
    
    def launch_browser(self, browser_name: str = "chrome", **options) -> Any:
        """Launch a browser instance with comprehensive error handling"""
        browser_name = browser_name.lower()
        
        # Check if session is already active
        if self.is_session_active():
            self.logger.info("Browser session already active")
            return self.active_driver
        
        # Clean up any stale sessions
        if self.active_driver:
            self.close_browser()
        
        # Validate browser support
        if browser_name not in self.available_browsers:
            missing_browsers = [browser_name]
            recommendations = self.support_manager.generate_setup_recommendations(missing_browsers)
            error_msg = f"Browser '{browser_name}' not found or not installed.\n{recommendations}"
            raise ValueError(error_msg)
        
        if not self.available_browsers[browser_name].is_installed:
            installation_guide = self.support_manager.get_installation_guide(browser_name)
            error_msg = f"Browser '{browser_name}' is not properly installed.\nInstallation Guide: {installation_guide}"
            raise ValueError(error_msg)
        
        # Validate framework compatibility
        is_supported, support_msg = self.support_manager.validate_browser_support(browser_name, self.framework)
        if not is_supported:
            raise ValueError(f"Framework compatibility issue: {support_msg}")
        
        # Attempt to launch browser with retries
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Launching {browser_name} (attempt {attempt + 1}/{max_retries})")
                
                if self.framework == "selenium":
                    driver = self._launch_selenium_browser(browser_name, **options)
                elif self.framework == "playwright":
                    driver = self._launch_playwright_browser(browser_name, **options)
                else:
                    raise ValueError(f"Unsupported framework: {self.framework}")
                
                # Verify browser launched successfully
                if self.is_session_active():
                    self.logger.info(f"✅ {browser_name} launched successfully")
                    return driver
                else:
                    raise WebDriverException("Browser launched but session is not active")
                    
            except (WebDriverException, SessionNotCreatedException) as e:
                last_error = e
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                # Clean up failed session
                if self.active_driver:
                    try:
                        self.close_browser()
                    except:
                        pass
                
                if attempt < max_retries - 1:
                    # Wait before retry
                    time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                last_error = e
                self.logger.error(f"Unexpected error during browser launch: {e}")
                break
        
        # All attempts failed
        troubleshooting = self.support_manager.get_troubleshooting_guide(browser_name, str(last_error))
        raise RuntimeError(f"Failed to launch {browser_name} after {max_retries} attempts.\n\n{troubleshooting}")
    
    def _launch_selenium_browser(self, browser_name: str, **options) -> webdriver:
        """Launch browser using Selenium"""
        try:
            if browser_name == "chrome":
                return self._launch_selenium_chrome(**options)
            elif browser_name == "firefox":
                return self._launch_selenium_firefox(**options)
            elif browser_name == "edge":
                return self._launch_selenium_edge(**options)
            else:
                raise ValueError(f"Selenium doesn't support {browser_name}")
        except Exception as e:
            self.logger.error(f"Failed to launch {browser_name} with Selenium: {e}")
            raise
    
    def _launch_selenium_chrome(self, **options) -> webdriver.Chrome:
        """Launch Chrome with Selenium and enhanced stability options"""
        chrome_options = ChromeOptions()
        
        # Headless mode
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        # Essential stability options
        stability_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage", 
            "--disable-gpu",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-images",
            "--disable-javascript-harmony-shipping",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-web-security",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--window-size=1920,1080",
            "--start-maximized",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        for arg in stability_args:
            chrome_options.add_argument(arg)
        
        # Performance and reliability preferences
        chrome_prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "popups": 2,
                "geolocation": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 2
            },
            "profile.default_content_settings": {
                "popups": 0
            }
        }
        chrome_options.add_experimental_option("prefs", chrome_prefs)
        
        # Additional experimental options for stability
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        
        # Add custom options
        for key, value in options.items():
            if key == "arguments":
                for arg in value:
                    chrome_options.add_argument(arg)
            elif key == "prefs":
                # Merge with default prefs
                chrome_prefs.update(value)
                chrome_options.add_experimental_option("prefs", chrome_prefs)
            elif key == "experimental_options":
                for opt_key, opt_value in value.items():
                    chrome_options.add_experimental_option(opt_key, opt_value)
        
        try:
            # Install and setup ChromeDriver
            service = ChromeService(ChromeDriverManager().install())
            
            # Launch browser
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Additional post-launch setup
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            # Execute JavaScript to remove automation detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.active_driver = driver
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to launch Chrome: {e}")
            raise
    
    def _launch_selenium_firefox(self, **options) -> webdriver.Firefox:
        """Launch Firefox with Selenium"""
        firefox_options = FirefoxOptions()
        
        if self.headless:
            firefox_options.add_argument("--headless")
        
        # Default options
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        
        # Add custom options
        for key, value in options.items():
            if key == "arguments":
                for arg in value:
                    firefox_options.add_argument(arg)
            elif key == "prefs":
                for pref_key, pref_value in value.items():
                    firefox_options.set_preference(pref_key, pref_value)
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
        self.active_driver = driver
        return driver
    
    def _launch_selenium_edge(self, **options) -> webdriver.Edge:
        """Launch Edge with Selenium"""
        edge_options = EdgeOptions()
        
        if self.headless:
            edge_options.add_argument("--headless=new")
        
        # Default options
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--window-size=1920,1080")
        
        # Add custom options
        for key, value in options.items():
            if key == "arguments":
                for arg in value:
                    edge_options.add_argument(arg)
            elif key == "prefs":
                edge_options.add_experimental_option("prefs", value)
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=edge_options)
        self.active_driver = driver
        return driver
    
    def _launch_playwright_browser(self, browser_name: str, **options):
        """Launch browser using Playwright"""
        try:
            if not self.playwright_context:
                self.playwright_context = sync_playwright().start()
            
            launch_options = {
                "headless": self.headless,
                **options
            }
            
            if browser_name == "chrome":
                browser = self.playwright_context.chromium.launch(**launch_options)
            elif browser_name == "firefox":
                browser = self.playwright_context.firefox.launch(**launch_options)
            elif browser_name == "edge":
                browser = self.playwright_context.chromium.launch(channel="msedge", **launch_options)
            elif browser_name == "safari":
                browser = self.playwright_context.webkit.launch(**launch_options)
            else:
                raise ValueError(f"Playwright doesn't support {browser_name}")
            
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            self.active_driver = {"browser": browser, "context": context, "page": page}
            return self.active_driver
            
        except Exception as e:
            self.logger.error(f"Failed to launch {browser_name} with Playwright: {e}")
            raise
    
    def close_browser(self):
        """Close the active browser instance with comprehensive cleanup"""
        if not self.active_driver:
            return
        
        with self.session_lock:
            try:
                self.logger.info("Closing browser session...")
                
                if self.framework == "selenium":
                    try:
                        # Try graceful shutdown first
                        self.active_driver.quit()
                    except Exception as e:
                        self.logger.warning(f"Graceful shutdown failed, forcing closure: {e}")
                        try:
                            # Force close if graceful fails
                            self.active_driver.close()
                        except:
                            pass
                
                elif self.framework == "playwright":
                    if isinstance(self.active_driver, dict):
                        try:
                            # Close page first
                            if 'page' in self.active_driver:
                                self.active_driver['page'].close()
                            
                            # Close context
                            if 'context' in self.active_driver:
                                self.active_driver['context'].close()
                            
                            # Close browser
                            if 'browser' in self.active_driver:
                                self.active_driver['browser'].close()
                                
                        except Exception as e:
                            self.logger.warning(f"Error closing Playwright components: {e}")
                        
                        # Stop Playwright context
                        if self.playwright_context:
                            try:
                                self.playwright_context.stop()
                            except Exception as e:
                                self.logger.warning(f"Error stopping Playwright context: {e}")
                            finally:
                                self.playwright_context = None
                
                self.logger.info("Browser session closed successfully")
                
            except Exception as e:
                self.logger.error(f"Error during browser cleanup: {e}")
            finally:
                self.active_driver = None
                self.last_activity = time.time()
    
    def force_cleanup(self):
        """Force cleanup of all browser processes"""
        self.logger.warning("Performing force cleanup of browser processes")
        
        try:
            # Kill any remaining browser processes
            import psutil
            browser_processes = ['chrome', 'chromium', 'firefox', 'msedge', 'safari']
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(browser in proc_name for browser in browser_processes):
                        if 'webdriver' in proc.cmdline() or 'automation' in ' '.join(proc.cmdline()):
                            proc.terminate()
                            self.logger.info(f"Terminated browser process: {proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error during force cleanup: {e}")
        
        # Reset state
        self.active_driver = None
        self.playwright_context = None
    
    def get_browser_recommendations(self) -> Dict[str, Any]:
        """Get browser installation recommendations"""
        available = list(self.available_browsers.keys())
        missing = []
        
        # Check for recommended browsers
        recommended_browsers = ['chrome', 'firefox', 'edge']
        for browser in recommended_browsers:
            if browser not in available:
                missing.append(browser)
        
        recommendations = {
            'available_browsers': available,
            'missing_browsers': missing,
            'recommended_browser': self.support_manager.get_recommended_browser(),
            'installation_guide': self.support_manager.generate_setup_recommendations(missing) if missing else None,
            'support_matrix': {
                name: self.support_manager.check_browser_compatibility(name)
                for name in recommended_browsers
            }
        }
        
        return recommendations
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive browser health check"""
        health_status = {
            'session_active': self.is_session_active(),
            'session_timeout': self.check_session_timeout(),
            'available_browsers': len(self.available_browsers),
            'framework': self.framework,
            'recommendations': self.get_browser_recommendations(),
            'last_activity': self.last_activity,
            'uptime': time.time() - self.last_activity if self.active_driver else 0
        }
        
        # Add browser-specific status
        if self.active_driver:
            try:
                if self.framework == "selenium":
                    health_status['current_url'] = self.active_driver.current_url
                    health_status['window_handles'] = len(self.active_driver.window_handles)
                elif self.framework == "playwright":
                    if isinstance(self.active_driver, dict) and 'page' in self.active_driver:
                        health_status['current_url'] = self.active_driver['page'].url
            except Exception as e:
                health_status['session_error'] = str(e)
                health_status['session_active'] = False
        
        return health_status
    
    def switch_framework(self, framework: str):
        """Switch between automation frameworks"""
        if self.active_driver:
            self.close_browser()
        
        self.framework = framework.lower()
        if self.framework not in ["selenium", "playwright"]:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def get_browser_capabilities(self, browser_name: str) -> Dict[str, Any]:
        """Get capabilities and features of a specific browser"""
        capabilities = {
            "chrome": {
                "supports_extensions": True,
                "supports_mobile_emulation": True,
                "supports_headless": True,
                "supports_screenshots": True,
                "supports_pdf_generation": True
            },
            "firefox": {
                "supports_extensions": True,
                "supports_mobile_emulation": False,
                "supports_headless": True,
                "supports_screenshots": True,
                "supports_pdf_generation": False
            },
            "edge": {
                "supports_extensions": True,
                "supports_mobile_emulation": True,
                "supports_headless": True,
                "supports_screenshots": True,
                "supports_pdf_generation": True
            },
            "safari": {
                "supports_extensions": False,
                "supports_mobile_emulation": False,
                "supports_headless": False,
                "supports_screenshots": True,
                "supports_pdf_generation": False
            }
        }
        
        return capabilities.get(browser_name.lower(), {})
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()