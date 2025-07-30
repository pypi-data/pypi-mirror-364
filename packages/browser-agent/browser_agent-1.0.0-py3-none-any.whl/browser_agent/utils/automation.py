import asyncio
import os
import time
import random
from typing import Dict, Any, Optional, List, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement

from ..core.config import Config


class WebAutomation:
    """Web automation utilities for browser interaction"""
    
    def __init__(self, driver, config: Config):
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(driver, config.page_load_timeout)
        
        # Set implicit wait
        self.driver.implicitly_wait(config.implicit_wait)
        
        # Create screenshots directory
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            self.driver.get(url)
            
            # Wait for page to load
            await asyncio.sleep(2)
            
            return {
                'success': True,
                'url': self.driver.current_url,
                'title': self.driver.title
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def click_element(self, selector: str) -> Dict[str, Any]:
        """Click an element using various selector methods"""
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                element = await self._find_element(selector)
                if not element:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        continue
                    return {
                        'success': False,
                        'error': f"Element not found after {max_retries} attempts: {selector}"
                    }
                
                # Check if element is clickable
                if not element.is_enabled():
                    return {
                        'success': False,
                        'error': f"Element is not clickable: {selector}"
                    }
                
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                await asyncio.sleep(0.5)
                
                # Wait for element to be stable
                await self._wait_for_element_stable(element)
                
                # Human-like click with slight delay
                if self.config.human_like_delays:
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Try different click methods
                try:
                    # Use ActionChains for more reliable clicking
                    actions = ActionChains(self.driver)
                    actions.move_to_element(element).click().perform()
                except Exception:
                    try:
                        # Fallback to regular click
                        element.click()
                    except Exception:
                        # Final fallback to JavaScript click
                        self.driver.execute_script("arguments[0].click();", element)
                
                return {
                    'success': True,
                    'element_tag': element.tag_name,
                    'element_text': element.text[:100],
                    'attempt': attempt + 1
                }
                
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
                    continue
                else:
                    return {
                        'success': False,
                        'error': f"Click failed after {max_retries} attempts: {str(e)}",
                        'attempts': max_retries
                    }
    
    async def type_text(self, selector: str, text: str, clear_first: bool = True) -> Dict[str, Any]:
        """Type text into an input element"""
        try:
            element = await self._find_element(selector)
            if not element:
                return {
                    'success': False,
                    'error': f"Element not found: {selector}"
                }
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            await asyncio.sleep(0.5)
            
            # Clear existing text if requested
            if clear_first:
                element.clear()
            
            # Human-like typing
            if self.config.human_like_delays:
                for char in text:
                    element.send_keys(char)
                    await asyncio.sleep(random.uniform(0.05, 0.15))
            else:
                element.send_keys(text)
            
            return {
                'success': True,
                'text_entered': text,
                'element_tag': element.tag_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def select_option(self, selector: str, option_value: str) -> Dict[str, Any]:
        """Select an option from a dropdown"""
        try:
            element = await self._find_element(selector)
            if not element:
                return {
                    'success': False,
                    'error': f"Element not found: {selector}"
                }
            
            select = Select(element)
            
            # Try different selection methods
            try:
                # Try by visible text first
                select.select_by_visible_text(option_value)
            except:
                try:
                    # Try by value
                    select.select_by_value(option_value)
                except:
                    # Try by index if it's a number
                    if option_value.isdigit():
                        select.select_by_index(int(option_value))
                    else:
                        raise Exception(f"Could not select option: {option_value}")
            
            return {
                'success': True,
                'selected_option': option_value,
                'available_options': [opt.text for opt in select.options]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def scroll(self, direction: str = "down", amount: Optional[str] = None) -> Dict[str, Any]:
        """Scroll the page or to a specific element"""
        try:
            if amount and amount.startswith(('id:', 'class:', 'css:', 'xpath:')):
                # Scroll to element
                element = await self._find_element(amount)
                if element:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    return {'success': True, 'scrolled_to': 'element'}
            
            # Scroll by direction
            if direction.lower() == "up":
                self.driver.execute_script("window.scrollBy(0, -500);")
            elif direction.lower() == "down":
                self.driver.execute_script("window.scrollBy(0, 500);")
            elif direction.lower() == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction.lower() == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            return {
                'success': True,
                'direction': direction
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def wait_for_element(self, selector: str, condition: str = "present", timeout: int = None) -> Dict[str, Any]:
        """Wait for an element to meet certain conditions"""
        try:
            timeout = timeout or self.config.page_load_timeout
            by, value = self._parse_selector(selector)
            
            # Handle None condition by defaulting to "present"
            if condition is None:
                condition = "present"
            
            # Handle common condition variations and aliases
            condition = condition.lower() if condition else "present"
            
            # Map common condition aliases
            condition_map = {
                "element_to_be_clickable": "clickable",
                "visibility": "visible",
                "presence": "present",
                "exists": "present"
            }
            condition = condition_map.get(condition, condition)
            
            if condition == "present":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
            elif condition == "visible":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by, value))
                )
            elif condition == "clickable":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, value))
                )
            else:
                return {
                    'success': False,
                    'error': f"Unknown condition: {condition}. Supported conditions: present, visible, clickable"
                }
            
            return {
                'success': True,
                'condition_met': condition,
                'element_found': True
            }
            
        except TimeoutException:
            return {
                'success': False,
                'error': f"Timeout waiting for element: {selector}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def extract_data(self, selector: str, data_type: str = "text") -> Dict[str, Any]:
        """Extract data from elements"""
        try:
            elements = await self._find_elements(selector)
            if not elements:
                return {
                    'success': False,
                    'error': f"No elements found: {selector}"
                }
            
            extracted_data = []
            for element in elements:
                if data_type == "text":
                    extracted_data.append(element.text)
                elif data_type == "href":
                    extracted_data.append(element.get_attribute("href"))
                elif data_type == "src":
                    extracted_data.append(element.get_attribute("src"))
                elif data_type == "value":
                    extracted_data.append(element.get_attribute("value"))
                else:
                    extracted_data.append(element.get_attribute(data_type))
            
            return {
                'success': True,
                'data': extracted_data,
                'count': len(extracted_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def verify_condition(self, condition: str, expected_value: str = None) -> Dict[str, Any]:
        """Verify various conditions on the page"""
        try:
            if condition.startswith("url_contains:"):
                expected = condition.split(":", 1)[1]
                current_url = self.driver.current_url
                success = expected in current_url
                return {
                    'success': success,
                    'condition': condition,
                    'current_value': current_url
                }
            
            elif condition.startswith("title_contains:"):
                expected = condition.split(":", 1)[1]
                current_title = self.driver.title
                success = expected in current_title
                return {
                    'success': success,
                    'condition': condition,
                    'current_value': current_title
                }
            
            elif condition.startswith("element_exists:"):
                selector = condition.split(":", 1)[1]
                element = await self._find_element(selector)
                success = element is not None
                return {
                    'success': success,
                    'condition': condition,
                    'element_found': success
                }
            
            elif condition.startswith("text_present:"):
                text = condition.split(":", 1)[1]
                page_source = self.driver.page_source
                success = text in page_source
                return {
                    'success': success,
                    'condition': condition,
                    'text_found': success
                }
            
            else:
                return {
                    'success': False,
                    'error': f"Unknown condition: {condition}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def take_screenshot(self, filename: str = None) -> Optional[str]:
        """Take a screenshot of the current page"""
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}"
            
            if not filename.endswith('.png'):
                filename += '.png'
            
            filepath = os.path.join(self.screenshot_dir, filename)
            self.driver.save_screenshot(filepath)
            
            return filepath
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None
    
    async def get_current_url(self) -> str:
        """Get current page URL"""
        return self.driver.current_url
    
    async def get_page_title(self) -> str:
        """Get current page title"""
        return self.driver.title
    
    async def get_page_source(self) -> str:
        """Get current page source"""
        return self.driver.page_source
    
    async def _find_element(self, selector: str) -> Optional[WebElement]:
        """Find a single element using various selector methods"""
        try:
            by, value = self._parse_selector(selector)
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            return None
        except Exception:
            return None
    
    async def _find_elements(self, selector: str) -> List[WebElement]:
        """Find multiple elements using various selector methods"""
        try:
            by, value = self._parse_selector(selector)
            return self.driver.find_elements(by, value)
        except Exception:
            return []
    
    async def _wait_for_element_stable(self, element, timeout: int = 5):
        """Wait for element to be stable (not moving/changing)"""
        start_time = time.time()
        last_location = None
        stable_count = 0
        
        while time.time() - start_time < timeout:
            try:
                current_location = element.location
                if last_location == current_location:
                    stable_count += 1
                    if stable_count >= 3:  # Element stable for 3 checks
                        break
                else:
                    stable_count = 0
                
                last_location = current_location
                await asyncio.sleep(0.1)
                
            except Exception:
                # Element may have become stale
                break
    
    def _parse_selector(self, selector: str) -> tuple:
        """Parse selector string into Selenium By and value"""
        if selector.startswith("id:"):
            return By.ID, selector[3:]
        elif selector.startswith("class:"):
            return By.CLASS_NAME, selector[6:]
        elif selector.startswith("css:"):
            return By.CSS_SELECTOR, selector[4:]
        elif selector.startswith("xpath:"):
            return By.XPATH, selector[6:]
        elif selector.startswith("name:"):
            return By.NAME, selector[5:]
        elif selector.startswith("tag:"):
            return By.TAG_NAME, selector[4:]
        elif selector.startswith("text:"):
            text = selector[5:]
            return By.XPATH, f"//*[contains(text(), '{text}')]"
        elif selector.startswith("link:"):
            text = selector[5:]
            return By.LINK_TEXT, text
        elif selector.startswith("partial_link:"):
            text = selector[13:]
            return By.PARTIAL_LINK_TEXT, text
        else:
            # Default to CSS selector if no prefix
            return By.CSS_SELECTOR, selector