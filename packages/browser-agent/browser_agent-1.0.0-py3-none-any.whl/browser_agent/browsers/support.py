"""
Browser Support and Installation Guide

This module provides comprehensive browser support detection, validation,
and installation guidance for the Browser Agent system.
"""

import os
import platform
import subprocess
import urllib.request
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class BrowserSupport(Enum):
    """Browser support levels"""
    FULLY_SUPPORTED = "fully_supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    NOT_SUPPORTED = "not_supported"
    RECOMMENDED = "recommended"


@dataclass
class SupportedBrowser:
    """Information about a supported browser"""
    name: str
    display_name: str
    support_level: BrowserSupport
    selenium_support: bool
    playwright_support: bool
    installation_guide: Dict[str, str]
    download_urls: Dict[str, str]
    automation_features: List[str]
    known_issues: List[str] = None


class BrowserSupportManager:
    """Manages browser support information and installation guidance"""
    
    # Comprehensive browser support matrix
    SUPPORTED_BROWSERS = {
        'chrome': SupportedBrowser(
            name='chrome',
            display_name='Google Chrome',
            support_level=BrowserSupport.RECOMMENDED,
            selenium_support=True,
            playwright_support=True,
            installation_guide={
                'windows': 'Download from https://www.google.com/chrome/ and run the installer',
                'darwin': 'Download from https://www.google.com/chrome/ or use: brew install --cask google-chrome',
                'linux': 'sudo apt update && sudo apt install google-chrome-stable'
            },
            download_urls={
                'windows': 'https://www.google.com/chrome/',
                'darwin': 'https://www.google.com/chrome/',
                'linux': 'https://www.google.com/chrome/'
            },
            automation_features=[
                'Full automation support',
                'Extensions support',
                'Mobile device emulation',
                'Headless mode',
                'Screenshot capture',
                'PDF generation',
                'Performance monitoring'
            ],
            known_issues=[]
        ),
        
        'chromium': SupportedBrowser(
            name='chromium',
            display_name='Chromium',
            support_level=BrowserSupport.FULLY_SUPPORTED,
            selenium_support=True,
            playwright_support=True,
            installation_guide={
                'windows': 'Download from https://www.chromium.org/getting-involved/download-chromium/',
                'darwin': 'brew install --cask chromium',
                'linux': 'sudo apt update && sudo apt install chromium-browser'
            },
            download_urls={
                'windows': 'https://www.chromium.org/getting-involved/download-chromium/',
                'darwin': 'https://www.chromium.org/getting-involved/download-chromium/',
                'linux': 'https://www.chromium.org/getting-involved/download-chromium/'
            },
            automation_features=[
                'Full automation support',
                'Open source',
                'Headless mode',
                'Screenshot capture',
                'Mobile device emulation'
            ]
        ),
        
        'firefox': SupportedBrowser(
            name='firefox',
            display_name='Mozilla Firefox',
            support_level=BrowserSupport.FULLY_SUPPORTED,
            selenium_support=True,
            playwright_support=True,
            installation_guide={
                'windows': 'Download from https://www.mozilla.org/firefox/',
                'darwin': 'Download from https://www.mozilla.org/firefox/ or use: brew install --cask firefox',
                'linux': 'sudo apt update && sudo apt install firefox'
            },
            download_urls={
                'windows': 'https://www.mozilla.org/firefox/',
                'darwin': 'https://www.mozilla.org/firefox/',
                'linux': 'https://www.mozilla.org/firefox/'
            },
            automation_features=[
                'Full automation support',
                'Extensions support',
                'Headless mode',
                'Screenshot capture',
                'Privacy features'
            ]
        ),
        
        'edge': SupportedBrowser(
            name='edge',
            display_name='Microsoft Edge',
            support_level=BrowserSupport.FULLY_SUPPORTED,
            selenium_support=True,
            playwright_support=True,
            installation_guide={
                'windows': 'Pre-installed on Windows 10+, or download from https://www.microsoft.com/edge',
                'darwin': 'Download from https://www.microsoft.com/edge',
                'linux': 'curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && sudo install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/ && sudo sh -c \'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/microsoft.gpg] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge-dev.list\' && sudo apt update && sudo apt install microsoft-edge-stable'
            },
            download_urls={
                'windows': 'https://www.microsoft.com/edge',
                'darwin': 'https://www.microsoft.com/edge',
                'linux': 'https://www.microsoft.com/edge'
            },
            automation_features=[
                'Full automation support',
                'Extensions support',
                'Mobile device emulation',
                'Headless mode',
                'Screenshot capture',
                'Enterprise features'
            ]
        ),
        
        'brave': SupportedBrowser(
            name='brave',
            display_name='Brave Browser',
            support_level=BrowserSupport.PARTIALLY_SUPPORTED,
            selenium_support=True,
            playwright_support=False,
            installation_guide={
                'windows': 'Download from https://brave.com/',
                'darwin': 'Download from https://brave.com/ or use: brew install --cask brave-browser',
                'linux': 'sudo apt install apt-transport-https curl && sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg && echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main"|sudo tee /etc/apt/sources.list.d/brave-browser-release.list && sudo apt update && sudo apt install brave-browser'
            },
            download_urls={
                'windows': 'https://brave.com/',
                'darwin': 'https://brave.com/',
                'linux': 'https://brave.com/'
            },
            automation_features=[
                'Selenium automation support',
                'Privacy-focused',
                'Ad blocking',
                'Crypto wallet integration'
            ],
            known_issues=[
                'Limited Playwright support',
                'Some automation features may be blocked by privacy settings'
            ]
        ),
        
        'safari': SupportedBrowser(
            name='safari',
            display_name='Safari',
            support_level=BrowserSupport.PARTIALLY_SUPPORTED,
            selenium_support=False,
            playwright_support=True,
            installation_guide={
                'darwin': 'Pre-installed on macOS. Enable Developer menu: Safari > Preferences > Advanced > Show Develop menu'
            },
            download_urls={
                'darwin': 'Pre-installed on macOS'
            },
            automation_features=[
                'Playwright automation support',
                'WebDriver support (limited)',
                'iOS device testing'
            ],
            known_issues=[
                'Limited Selenium support',
                'Requires developer mode for automation',
                'macOS only'
            ]
        )
    }
    
    def __init__(self):
        self.system = platform.system().lower()
        
    def get_recommended_browser(self) -> str:
        """Get the recommended browser for this system"""
        # Chrome is recommended for all platforms
        return 'chrome'
    
    def get_supported_browsers(self) -> Dict[str, SupportedBrowser]:
        """Get all supported browsers for the current system"""
        supported = {}
        
        for name, browser in self.SUPPORTED_BROWSERS.items():
            # Check if browser has installation guide for current system
            if self.system in browser.installation_guide:
                supported[name] = browser
            # Safari is only for macOS
            elif name == 'safari' and self.system == 'darwin':
                supported[name] = browser
                
        return supported
    
    def get_browser_info(self, browser_name: str) -> Optional[SupportedBrowser]:
        """Get detailed information about a browser"""
        return self.SUPPORTED_BROWSERS.get(browser_name.lower())
    
    def get_installation_guide(self, browser_name: str) -> Optional[str]:
        """Get installation instructions for a browser"""
        browser = self.get_browser_info(browser_name)
        if browser and self.system in browser.installation_guide:
            return browser.installation_guide[self.system]
        return None
    
    def validate_browser_support(self, browser_name: str, framework: str = 'selenium') -> Tuple[bool, str]:
        """Validate if a browser is supported with the given framework"""
        browser = self.get_browser_info(browser_name)
        
        if not browser:
            return False, f"Browser '{browser_name}' is not supported"
        
        if framework.lower() == 'selenium' and not browser.selenium_support:
            return False, f"{browser.display_name} does not support Selenium automation"
        
        if framework.lower() == 'playwright' and not browser.playwright_support:
            return False, f"{browser.display_name} does not support Playwright automation"
        
        if browser.support_level == BrowserSupport.NOT_SUPPORTED:
            return False, f"{browser.display_name} is not supported for automation"
        
        return True, f"{browser.display_name} is supported with {framework}"
    
    def generate_setup_recommendations(self, missing_browsers: List[str]) -> str:
        """Generate setup recommendations for missing browsers"""
        if not missing_browsers:
            return "✅ All recommended browsers are available!"
        
        recommendations = []
        recommendations.append("🔧 Browser Setup Recommendations")
        recommendations.append("=" * 40)
        
        # Always recommend Chrome first
        if 'chrome' in missing_browsers:
            chrome_guide = self.get_installation_guide('chrome')
            recommendations.append(f"\n🥇 **RECOMMENDED: Google Chrome**")
            recommendations.append(f"   Installation: {chrome_guide}")
            recommendations.append(f"   Reason: Best automation support, most stable")
        
        # Alternative browsers
        alternatives = []
        for browser_name in missing_browsers:
            if browser_name != 'chrome':
                browser = self.get_browser_info(browser_name)
                if browser:
                    guide = self.get_installation_guide(browser_name)
                    alternatives.append(f"\n🔄 **Alternative: {browser.display_name}**")
                    alternatives.append(f"   Installation: {guide}")
                    alternatives.append(f"   Support Level: {browser.support_level.value}")
        
        if alternatives:
            recommendations.append(f"\n📋 **Alternative Options:**")
            recommendations.extend(alternatives)
        
        # Quick setup commands
        recommendations.append(f"\n⚡ **Quick Setup (if available):**")
        if self.system == 'darwin':
            recommendations.append("   brew install --cask google-chrome")
        elif self.system == 'linux':
            recommendations.append("   sudo apt update && sudo apt install google-chrome-stable")
        
        recommendations.append(f"\n💡 **Tips:**")
        recommendations.append("   - Chrome provides the most reliable automation experience")
        recommendations.append("   - Chromium is a good open-source alternative")
        recommendations.append("   - Firefox offers excellent privacy features")
        recommendations.append("   - Avoid Safari unless specifically testing for iOS/macOS")
        
        return "\n".join(recommendations)
    
    def check_browser_compatibility(self, browser_name: str) -> Dict[str, Any]:
        """Check comprehensive browser compatibility"""
        browser = self.get_browser_info(browser_name)
        
        if not browser:
            return {
                'supported': False,
                'reason': f"Browser '{browser_name}' is not in our supported list",
                'alternatives': [self.get_recommended_browser()]
            }
        
        compatibility = {
            'supported': True,
            'browser': browser,
            'selenium_support': browser.selenium_support,
            'playwright_support': browser.playwright_support,
            'automation_features': browser.automation_features,
            'known_issues': browser.known_issues or [],
            'installation_available': self.system in browser.installation_guide,
            'support_level': browser.support_level.value
        }
        
        # Add warnings for partially supported browsers
        if browser.support_level == BrowserSupport.PARTIALLY_SUPPORTED:
            compatibility['warnings'] = [
                f"{browser.display_name} has limited automation support",
                "Some features may not work as expected",
                "Consider using Chrome for best results"
            ]
        
        return compatibility
    
    def get_troubleshooting_guide(self, browser_name: str, error: str = None) -> str:
        """Get troubleshooting guide for browser issues"""
        browser = self.get_browser_info(browser_name)
        
        guide = [f"🔧 Troubleshooting Guide for {browser.display_name if browser else browser_name}"]
        guide.append("=" * 50)
        
        if error:
            guide.append(f"\n❌ Error: {error}")
        
        if browser_name.lower() == 'chrome':
            guide.extend([
                "\n🔍 Common Chrome Issues:",
                "1. **Driver Version Mismatch**",
                "   - The system will auto-download the correct ChromeDriver",
                "   - If issues persist, clear driver cache: rm -rf ~/.wdm/",
                "",
                "2. **Permission Issues**",
                "   - macOS: Grant Terminal accessibility permissions",
                "   - Linux: Add user to required groups",
                "",
                "3. **Window Closed Error**",
                "   - Browser crashed or was manually closed",
                "   - Solution: Restart the automation session",
                "",
                "4. **Element Not Found**",
                "   - Page may still be loading",
                "   - Increase timeout settings",
                "   - Check if element selector is correct"
            ])
        
        elif browser_name.lower() == 'firefox':
            guide.extend([
                "\n🔍 Common Firefox Issues:",
                "1. **GeckoDriver Issues**",
                "   - Auto-downloaded by webdriver-manager",
                "   - Manual install: https://github.com/mozilla/geckodriver/releases",
                "",
                "2. **Profile Problems**",
                "   - Firefox may create temporary profiles",
                "   - Clear profile cache if needed",
                "",
                "3. **Extension Conflicts**",
                "   - Disable extensions that might interfere",
                "   - Use clean profile for automation"
            ])
        
        guide.extend([
            f"\n🛠️ General Solutions:",
            "1. **Restart Browser Agent**",
            "   - Close all browser instances",
            "   - Restart the GUI application",
            "",
            "2. **Update Browser**",
            "   - Ensure you have the latest browser version",
            "   - WebDriver versions are matched automatically",
            "",
            "3. **Check System Requirements**",
            "   - Sufficient RAM (4GB+ recommended)",
            "   - Updated operating system",
            "   - Stable internet connection",
            "",
            "4. **Alternative Browser**",
            f"   - Try using {self.get_recommended_browser()} instead",
            "   - Different browsers may work better on different systems"
        ])
        
        return "\n".join(guide)


def get_browser_support_manager() -> BrowserSupportManager:
    """Get the browser support manager instance"""
    return BrowserSupportManager()