import asyncio
import time
from typing import Dict, Any, Optional, List, Union
from enum import Enum

from .automation import WebAutomation
from .desktop_automation import DesktopAutomation
from ..core.config import Config


class AutomationType(Enum):
    """Types of automation actions"""
    BROWSER = "browser"
    DESKTOP = "desktop"
    HYBRID = "hybrid"


class UnifiedAutomation:
    """Unified automation manager that seamlessly combines browser and desktop control"""
    
    def __init__(self, driver=None, config: Config = None):
        self.config = config or Config()
        self.web_automation = WebAutomation(driver, self.config) if driver else None
        self.desktop_automation = DesktopAutomation(self.config)
        
        # Task execution history
        self.execution_history = []
        
    def set_browser_driver(self, driver):
        """Set or update the browser driver for web automation"""
        self.web_automation = WebAutomation(driver, self.config)
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a unified automation task"""
        task_type = task.get('type', 'browser')
        action = task.get('action')
        params = task.get('params', {})
        
        start_time = time.time()
        
        try:
            if task_type == 'browser':
                result = await self._execute_browser_task(action, params)
            elif task_type == 'desktop':
                result = await self._execute_desktop_task(action, params)
            elif task_type == 'hybrid':
                result = await self._execute_hybrid_task(action, params)
            else:
                result = {
                    'success': False,
                    'error': f"Unknown task type: {task_type}"
                }
            
            # Add execution metadata
            result['execution_time'] = time.time() - start_time
            result['task_type'] = task_type
            result['action'] = action
            
            # Store in history
            self.execution_history.append({
                'task': task,
                'result': result,
                'timestamp': time.time()
            })
            
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time,
                'task_type': task_type,
                'action': action
            }
            
            self.execution_history.append({
                'task': task,
                'result': error_result,
                'timestamp': time.time()
            })
            
            return error_result
    
    async def _execute_browser_task(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute browser-specific automation task"""
        if not self.web_automation:
            return {
                'success': False,
                'error': "Browser driver not initialized"
            }
        
        if action == 'navigate':
            return await self.web_automation.navigate(params.get('url'))
        elif action == 'click':
            return await self.web_automation.click_element(params.get('selector'))
        elif action == 'type':
            return await self.web_automation.type_text(
                params.get('selector'),
                params.get('text'),
                params.get('clear_first', True)
            )
        elif action == 'select':
            return await self.web_automation.select_option(
                params.get('selector'),
                params.get('option')
            )
        elif action == 'scroll':
            return await self.web_automation.scroll(
                params.get('direction', 'down'),
                params.get('amount')
            )
        elif action == 'screenshot':
            return await self.web_automation.take_screenshot(params.get('filename'))
        elif action == 'wait':
            return await self.web_automation.wait_for_element(
                params.get('selector'),
                params.get('timeout', 10)
            )
        elif action == 'extract':
            return await self.web_automation.extract_text(params.get('selector'))
        else:
            return {
                'success': False,
                'error': f"Unknown browser action: {action}"
            }
    
    async def _execute_desktop_task(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute desktop-specific automation task"""
        if action == 'click_coordinates':
            return await self.desktop_automation.click_at_coordinates(
                params.get('x'),
                params.get('y'),
                params.get('button', 'left'),
                params.get('clicks', 1)
            )
        elif action == 'click_image':
            return await self.desktop_automation.find_and_click_image(
                params.get('image_path'),
                params.get('confidence', 0.8),
                params.get('region')
            )
        elif action == 'type':
            return await self.desktop_automation.type_text(
                params.get('text'),
                params.get('interval')
            )
        elif action == 'press_key':
            return await self.desktop_automation.press_key(
                params.get('key'),
                params.get('presses', 1)
            )
        elif action == 'scroll':
            return await self.desktop_automation.scroll(
                params.get('clicks'),
                params.get('x'),
                params.get('y')
            )
        elif action == 'drag_drop':
            return await self.desktop_automation.drag_and_drop(
                params.get('start_x'),
                params.get('start_y'),
                params.get('end_x'),
                params.get('end_y'),
                params.get('duration', 1.0)
            )
        elif action == 'open_app':
            return await self.desktop_automation.open_application(params.get('app_name'))
        elif action == 'screenshot':
            return await self.desktop_automation.take_screenshot(params.get('region'))
        elif action == 'move_mouse':
            return await self.desktop_automation.move_mouse(
                params.get('x'),
                params.get('y'),
                params.get('duration', 0.5)
            )
        elif action == 'wait_for_image':
            return await self.desktop_automation.wait_for_image(
                params.get('image_path'),
                params.get('timeout', 10),
                params.get('confidence', 0.8)
            )
        elif action == 'get_mouse_position':
            return await self.desktop_automation.get_mouse_position()
        elif action == 'get_screen_info':
            return await self.desktop_automation.get_screen_info()
        else:
            return {
                'success': False,
                'error': f"Unknown desktop action: {action}"
            }
    
    async def _execute_hybrid_task(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute hybrid tasks that combine browser and desktop automation"""
        if action == 'browser_to_desktop':
            # Take screenshot of browser, then interact with desktop
            browser_result = await self._execute_browser_task('screenshot', {})
            if not browser_result['success']:
                return browser_result
            
            # Switch to desktop interaction
            desktop_params = params.get('desktop_params', {})
            desktop_action = params.get('desktop_action')
            return await self._execute_desktop_task(desktop_action, desktop_params)
        
        elif action == 'desktop_to_browser':
            # Perform desktop action, then browser action
            desktop_params = params.get('desktop_params', {})
            desktop_action = params.get('desktop_action')
            desktop_result = await self._execute_desktop_task(desktop_action, desktop_params)
            
            if not desktop_result['success']:
                return desktop_result
            
            # Switch to browser interaction
            browser_params = params.get('browser_params', {})
            browser_action = params.get('browser_action')
            return await self._execute_browser_task(browser_action, browser_params)
        
        elif action == 'copy_from_browser_to_desktop':
            # Extract text from browser and type it in desktop app
            extract_result = await self._execute_browser_task('extract', {
                'selector': params.get('browser_selector')
            })
            
            if not extract_result['success']:
                return extract_result
            
            # Type the extracted text in desktop
            return await self._execute_desktop_task('type', {
                'text': extract_result.get('text', '')
            })
        
        elif action == 'drag_from_browser_to_desktop':
            # Complex drag operation from browser to desktop application
            # This would require more sophisticated coordination
            return {
                'success': False,
                'error': "Drag from browser to desktop not yet implemented"
            }
        
        else:
            return {
                'success': False,
                'error': f"Unknown hybrid action: {action}"
            }
    
    async def execute_sequence(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a sequence of automation tasks"""
        results = []
        total_start_time = time.time()
        
        for i, task in enumerate(tasks):
            result = await self.execute_task(task)
            results.append(result)
            
            # Stop execution if a task fails and stop_on_error is True
            if not result['success'] and task.get('stop_on_error', False):
                return {
                    'success': False,
                    'error': f"Task {i+1} failed: {result.get('error')}",
                    'completed_tasks': i,
                    'total_tasks': len(tasks),
                    'results': results,
                    'total_execution_time': time.time() - total_start_time
                }
            
            # Add delay between tasks if specified
            delay = task.get('delay_after', 0)
            if delay > 0:
                await asyncio.sleep(delay)
        
        # Calculate success rate
        successful_tasks = sum(1 for result in results if result['success'])
        success_rate = successful_tasks / len(tasks) if tasks else 0
        
        return {
            'success': success_rate > 0.5,  # Consider successful if more than 50% tasks succeed
            'completed_tasks': len(tasks),
            'successful_tasks': successful_tasks,
            'success_rate': success_rate,
            'results': results,
            'total_execution_time': time.time() - total_start_time
        }
    
    def get_execution_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get execution history"""
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history
    
    def clear_execution_history(self):
        """Clear execution history"""
        self.execution_history.clear()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get available automation capabilities"""
        return {
            'browser_automation': self.web_automation is not None,
            'desktop_automation': True,
            'hybrid_automation': True,
            'browser_actions': [
                'navigate', 'click', 'type', 'select', 'scroll', 
                'screenshot', 'wait', 'extract'
            ],
            'desktop_actions': [
                'click_coordinates', 'click_image', 'type', 'press_key',
                'scroll', 'drag_drop', 'open_app', 'screenshot',
                'move_mouse', 'wait_for_image', 'get_mouse_position',
                'get_screen_info'
            ],
            'hybrid_actions': [
                'browser_to_desktop', 'desktop_to_browser',
                'copy_from_browser_to_desktop'
            ]
        }