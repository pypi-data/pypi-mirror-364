import os
import platform
import subprocess
import shutil
from typing import Dict, List, Optional
from dataclasses import dataclass
import psutil


@dataclass
class BrowserInfo:
    name: str
    executable_path: str
    version: Optional[str] = None
    is_installed: bool = True


class BrowserDetector:
    """Detects installed browsers on the system"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.browsers = {}
        
    def detect_all(self) -> Dict[str, BrowserInfo]:
        """Detect all available browsers on the system"""
        detection_methods = {
            'chrome': self._detect_chrome,
            'firefox': self._detect_firefox,
            'edge': self._detect_edge,
            'safari': self._detect_safari,
            'opera': self._detect_opera,
        }
        
        for browser_name, detect_func in detection_methods.items():
            try:
                browser_info = detect_func()
                if browser_info and browser_info.is_installed:
                    self.browsers[browser_name] = browser_info
            except Exception as e:
                print(f"Error detecting {browser_name}: {e}")
                
        return self.browsers
    
    def _detect_chrome(self) -> Optional[BrowserInfo]:
        """Detect Google Chrome"""
        paths = self._get_chrome_paths()
        
        for path in paths:
            if os.path.exists(path):
                version = self._get_browser_version(path)
                return BrowserInfo("Chrome", path, version)
        
        # Try using which/where command
        executable = shutil.which('google-chrome') or shutil.which('chrome')
        if executable:
            version = self._get_browser_version(executable)
            return BrowserInfo("Chrome", executable, version)
            
        return BrowserInfo("Chrome", "", None, False)
    
    def _detect_firefox(self) -> Optional[BrowserInfo]:
        """Detect Mozilla Firefox"""
        paths = self._get_firefox_paths()
        
        for path in paths:
            if os.path.exists(path):
                version = self._get_browser_version(path)
                return BrowserInfo("Firefox", path, version)
        
        executable = shutil.which('firefox')
        if executable:
            version = self._get_browser_version(executable)
            return BrowserInfo("Firefox", executable, version)
            
        return BrowserInfo("Firefox", "", None, False)
    
    def _detect_edge(self) -> Optional[BrowserInfo]:
        """Detect Microsoft Edge"""
        paths = self._get_edge_paths()
        
        for path in paths:
            if os.path.exists(path):
                version = self._get_browser_version(path)
                return BrowserInfo("Edge", path, version)
        
        executable = shutil.which('msedge') or shutil.which('microsoft-edge')
        if executable:
            version = self._get_browser_version(executable)
            return BrowserInfo("Edge", executable, version)
            
        return BrowserInfo("Edge", "", None, False)
    
    def _detect_safari(self) -> Optional[BrowserInfo]:
        """Detect Safari (macOS only)"""
        if self.system != 'darwin':
            return BrowserInfo("Safari", "", None, False)
        
        safari_path = "/Applications/Safari.app/Contents/MacOS/Safari"
        if os.path.exists(safari_path):
            version = self._get_safari_version()
            return BrowserInfo("Safari", safari_path, version)
            
        return BrowserInfo("Safari", "", None, False)
    
    def _detect_opera(self) -> Optional[BrowserInfo]:
        """Detect Opera"""
        paths = self._get_opera_paths()
        
        for path in paths:
            if os.path.exists(path):
                version = self._get_browser_version(path)
                return BrowserInfo("Opera", path, version)
        
        executable = shutil.which('opera')
        if executable:
            version = self._get_browser_version(executable)
            return BrowserInfo("Opera", executable, version)
            
        return BrowserInfo("Opera", "", None, False)
    
    def _get_chrome_paths(self) -> List[str]:
        """Get possible Chrome installation paths"""
        if self.system == 'windows':
            return [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ]
        elif self.system == 'darwin':
            return [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            ]
        else:  # Linux
            return [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
    
    def _get_firefox_paths(self) -> List[str]:
        """Get possible Firefox installation paths"""
        if self.system == 'windows':
            return [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
        elif self.system == 'darwin':
            return [
                "/Applications/Firefox.app/Contents/MacOS/firefox"
            ]
        else:  # Linux
            return [
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr"
            ]
    
    def _get_edge_paths(self) -> List[str]:
        """Get possible Edge installation paths"""
        if self.system == 'windows':
            return [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
        elif self.system == 'darwin':
            return [
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            ]
        else:  # Linux
            return [
                "/usr/bin/microsoft-edge-stable",
                "/usr/bin/microsoft-edge"
            ]
    
    def _get_opera_paths(self) -> List[str]:
        """Get possible Opera installation paths"""
        if self.system == 'windows':
            return [
                r"C:\Program Files\Opera\opera.exe",
                r"C:\Program Files (x86)\Opera\opera.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Opera\opera.exe")
            ]
        elif self.system == 'darwin':
            return [
                "/Applications/Opera.app/Contents/MacOS/Opera"
            ]
        else:  # Linux
            return [
                "/usr/bin/opera",
                "/usr/bin/opera-stable"
            ]
    
    def _get_browser_version(self, path: str) -> Optional[str]:
        """Get browser version using command line"""
        try:
            if 'chrome' in path.lower():
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
            elif 'firefox' in path.lower():
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
            elif 'edge' in path.lower() or 'msedge' in path.lower():
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
            elif 'opera' in path.lower():
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
            else:
                return None
                
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def _get_safari_version(self) -> Optional[str]:
        """Get Safari version on macOS"""
        try:
            result = subprocess.run(
                ['mdls', '-name', 'kMDItemVersion', '/Applications/Safari.app'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.strip()
                # Extract version from 'kMDItemVersion = "X.X.X"'
                if '=' in version_line:
                    version = version_line.split('=')[1].strip().strip('"')
                    return f"Safari {version}"
        except Exception:
            pass
        return None
    
    def get_running_browsers(self) -> List[str]:
        """Get list of currently running browsers"""
        running = []
        browser_processes = {
            'chrome': ['chrome', 'google-chrome', 'chromium'],
            'firefox': ['firefox'],
            'edge': ['msedge', 'microsoft-edge'],
            'safari': ['Safari'],
            'opera': ['opera']
        }
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                for browser, process_names in browser_processes.items():
                    if any(name in proc_name for name in process_names):
                        if browser not in running:
                            running.append(browser)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return running