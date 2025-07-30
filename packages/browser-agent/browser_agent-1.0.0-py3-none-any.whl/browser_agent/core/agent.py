import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .config import Config
from .multi_llm_processor import MultiLLMProcessor, TaskPlan, TaskStep
from ..browsers.manager import BrowserManager
from ..utils.automation import WebAutomation
from ..utils.unified_automation import UnifiedAutomation
from ..utils.logger import setup_logging


@dataclass
class ExecutionResult:
    success: bool
    step_results: List[Dict[str, Any]]
    error_message: Optional[str] = None
    screenshots: List[str] = None
    execution_time: float = 0.0


class BrowserAgent:
    """Main browser automation agent with AI capabilities"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.config.validate()
        
        # Setup logging
        self.logger = setup_logging(self.config.log_level, self.config.log_file)
        
        # Initialize components
        self.ai_processor = MultiLLMProcessor(self.config)
        self.browser_manager = BrowserManager(
            headless=self.config.headless,
            framework=self.config.automation_framework
        )
        self.automation = None
        self.unified_automation = UnifiedAutomation(config=self.config)
        self.current_task = None
        
    async def execute_task(self, user_prompt: str, browser: str = None) -> ExecutionResult:
        """Execute a task based on user prompt"""
        start_time = time.time()
        browser = browser or self.config.default_browser
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Starting task: {user_prompt}")
                
                # Ensure browser session is healthy
                if not await self._ensure_browser_session(browser):
                    raise RuntimeError("Failed to establish browser session")
                
                # Process user prompt into task plan
                context = await self._get_current_context()
                task_plan = await self.ai_processor.process_prompt(user_prompt, context)
                self.current_task = task_plan
                
                self.logger.info(f"Generated plan with {len(task_plan.steps)} steps")
                
                # Execute task plan
                execution_result = await self._execute_task_plan(task_plan)
                execution_result.execution_time = time.time() - start_time
                
                return execution_result
                
            except Exception as e:
                self.logger.error(f"Task execution failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                # Try to recover from browser session issues
                if "session" in str(e).lower() or "chrome" in str(e).lower():
                    self.logger.info("Attempting browser session recovery...")
                    await self._recover_browser_session(browser)
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)  # Wait before retry
                        continue
                
                return ExecutionResult(
                    success=False,
                    step_results=[],
                    error_message=str(e),
                    execution_time=time.time() - start_time
                )
    
    async def _execute_task_plan(self, task_plan: TaskPlan) -> ExecutionResult:
        """Execute the task plan step by step"""
        step_results = []
        screenshots = []
        
        self.logger.info(f"Executing task: {task_plan.objective}")
        
        for i, step in enumerate(task_plan.steps):
            try:
                self.logger.info(f"Step {i+1}/{len(task_plan.steps)}: {step.description}")
                
                # Execute the step
                step_result = await self._execute_step(step)
                step_results.append(step_result)
                
                # Take screenshot if configured or on error
                if self.config.screenshot_on_error or step_result.get('screenshot_requested'):
                    screenshot_path = await self.automation.take_screenshot(
                        f"step_{i+1}_{step.action}"
                    )
                    if screenshot_path:
                        screenshots.append(screenshot_path)
                
                # Check if step failed
                if not step_result.get('success', True):
                    error_msg = step_result.get('error', 'Step execution failed')
                    self.logger.error(f"Step {i+1} failed: {error_msg}")
                    
                    # Try to recover or adapt plan
                    if not await self._handle_step_failure(step, step_result, i):
                        return ExecutionResult(
                            success=False,
                            step_results=step_results,
                            error_message=f"Step {i+1} failed: {error_msg}",
                            screenshots=screenshots
                        )
                
                # Human-like delay between steps
                if self.config.human_like_delays:
                    await asyncio.sleep(
                        self.config.min_delay + 
                        (self.config.max_delay - self.config.min_delay) * 0.5
                    )
                    
            except Exception as e:
                self.logger.error(f"Error executing step {i+1}: {e}")
                step_results.append({
                    'success': False,
                    'error': str(e),
                    'step': step.action
                })
                
                if self.config.screenshot_on_error:
                    screenshot_path = await self.automation.take_screenshot(f"error_step_{i+1}")
                    if screenshot_path:
                        screenshots.append(screenshot_path)
                
                return ExecutionResult(
                    success=False,
                    step_results=step_results,
                    error_message=f"Exception in step {i+1}: {e}",
                    screenshots=screenshots
                )
        
        # Verify success criteria
        success = await self._verify_success_criteria(task_plan.success_criteria)
        
        return ExecutionResult(
            success=success,
            step_results=step_results,
            screenshots=screenshots
        )
    
    async def _execute_step(self, step: TaskStep) -> Dict[str, Any]:
        """Execute a single step using unified automation"""
        try:
            # Ensure browser driver is set for unified automation if needed
            if step.automation_type in ['browser', 'hybrid'] and self.automation:
                self.unified_automation.set_browser_driver(self.automation.driver)
            
            # Create task for unified automation
            task = {
                'type': step.automation_type,
                'action': step.action,
                'params': {
                    'selector': step.target,
                    'text': step.value,
                    'option': step.value,
                    'url': step.target,
                    'filename': step.value,
                    'timeout': 10,
                    'direction': step.target,
                    'amount': step.value,
                    **(step.params or {})
                }
            }
            
            # Handle specific parameter mapping based on action
            if step.action == 'click_coordinates':
                task['params'].update({
                    'x': step.params.get('x', 0),
                    'y': step.params.get('y', 0),
                    'button': step.params.get('button', 'left'),
                    'clicks': step.params.get('clicks', 1)
                })
            elif step.action == 'click_image':
                task['params'].update({
                    'image_path': step.target,
                    'confidence': step.params.get('confidence', 0.8),
                    'region': step.params.get('region')
                })
            elif step.action == 'press_key':
                task['params'].update({
                    'key': step.target or step.params.get('key'),
                    'presses': step.params.get('presses', 1)
                })
            elif step.action == 'drag_drop':
                task['params'].update({
                    'start_x': step.params.get('start_x', 0),
                    'start_y': step.params.get('start_y', 0),
                    'end_x': step.params.get('end_x', 0),
                    'end_y': step.params.get('end_y', 0),
                    'duration': step.params.get('duration', 1.0)
                })
            elif step.action == 'open_app':
                task['params'].update({
                    'app_name': step.target or step.params.get('app_name')
                })
            elif step.action == 'move_mouse':
                task['params'].update({
                    'x': step.params.get('x', 0),
                    'y': step.params.get('y', 0),
                    'duration': step.params.get('duration', 0.5)
                })
            elif step.action == 'wait_for_image':
                task['params'].update({
                    'image_path': step.target,
                    'timeout': step.params.get('timeout', 10),
                    'confidence': step.params.get('confidence', 0.8)
                })
            
            # Execute the task
            result = await self.unified_automation.execute_task(task)
            
            # Add screenshot flag if this was a screenshot action
            if step.action == 'screenshot':
                result['screenshot_requested'] = True
            
            return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': step.action,
                'automation_type': step.automation_type
            }
    
    async def _handle_step_failure(self, step: TaskStep, result: Dict, step_index: int) -> bool:
        """Handle step failure and attempt recovery"""
        # Simple retry logic for now
        retry_actions = ['click', 'type', 'select']
        
        if step.action in retry_actions:
            self.logger.info(f"Retrying step {step_index + 1}: {step.action}")
            await asyncio.sleep(2)  # Wait before retry
            
            retry_result = await self._execute_step(step)
            if retry_result.get('success'):
                self.logger.info(f"Step {step_index + 1} succeeded on retry")
                return True
        
        return False
    
    async def _verify_success_criteria(self, criteria: List[str]) -> bool:
        """Verify that success criteria are met"""
        for criterion in criteria:
            try:
                # This is a simplified verification
                # In a real implementation, you'd parse the criterion and check accordingly
                result = await self.automation.verify_condition(criterion)
                if not result.get('success'):
                    self.logger.warning(f"Success criterion not met: {criterion}")
                    return False
            except Exception as e:
                self.logger.error(f"Error verifying criterion '{criterion}': {e}")
                return False
        
        return True
    
    async def _ensure_browser_session(self, browser: str) -> bool:
        """Ensure browser session is healthy and active"""
        try:
            # Check if session is active and healthy
            if self.browser_manager.is_session_active():
                # Verify automation is working
                if self.automation:
                    try:
                        await self.automation.get_current_url()
                        return True
                    except Exception:
                        self.logger.warning("Automation check failed, recreating session")
            
            # Launch new browser session
            self.logger.info(f"Launching new browser session: {browser}")
            driver = self.browser_manager.launch_browser(browser)
            self.automation = WebAutomation(driver, self.config)
            
            # Verify session is working
            await asyncio.sleep(1)
            return self.browser_manager.is_session_active()
            
        except Exception as e:
            self.logger.error(f"Failed to ensure browser session: {e}")
            return False
    
    async def _recover_browser_session(self, browser: str):
        """Recover from browser session issues"""
        try:
            self.logger.info("Recovering browser session...")
            
            # Close existing session
            if self.browser_manager.active_driver:
                self.browser_manager.close_browser()
            
            # Force cleanup if needed
            self.browser_manager.force_cleanup()
            
            # Wait a bit before relaunching
            await asyncio.sleep(2)
            
            # Try to relaunch
            await self._ensure_browser_session(browser)
            
        except Exception as e:
            self.logger.error(f"Browser session recovery failed: {e}")

    async def _get_current_context(self) -> Dict[str, Any]:
        """Get current browser context for AI processing"""
        if not self.automation:
            return {}
        
        try:
            context = {
                'current_url': await self.automation.get_current_url(),
                'page_title': await self.automation.get_page_title(),
            }
            
            # Get page content for analysis (limited to avoid token limits)
            page_source = await self.automation.get_page_source()
            if page_source:
                page_analysis = await self.ai_processor.analyze_page_content(
                    page_source[:10000],  # Limit content size
                    context['current_url']
                )
                context.update(page_analysis)
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error getting context: {e}")
            return {}
    
    def get_available_browsers(self) -> Dict[str, Any]:
        """Get list of available browsers"""
        return self.browser_manager.get_available_browsers()
    
    def switch_browser(self, browser_name: str):
        """Switch to a different browser"""
        if self.browser_manager.active_driver:
            self.browser_manager.close_browser()
        
        driver = self.browser_manager.launch_browser(browser_name)
        self.automation = WebAutomation(driver, self.config)
    
    def close(self):
        """Clean up resources"""
        if self.browser_manager:
            self.browser_manager.close_browser()
        self.logger.info("Browser agent closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()