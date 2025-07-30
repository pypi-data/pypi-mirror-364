import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dataclasses import dataclass

from .config import Config


@dataclass
class TaskStep:
    action: str
    target: Optional[str] = None
    value: Optional[str] = None
    condition: Optional[str] = None
    description: str = ""
    automation_type: str = "browser"  # browser, desktop, or hybrid
    params: Optional[Dict[str, Any]] = None  # Additional parameters for desktop/hybrid actions


@dataclass
class TaskPlan:
    objective: str
    steps: List[TaskStep]
    success_criteria: List[str]
    estimated_time: int = 0


class AIProcessor:
    """Processes user prompts and generates actionable browser automation plans"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        if not config.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.openai_client = OpenAI(api_key=config.openai_api_key)
        
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the AI"""
        return """You are an intelligent web browser automation agent. Your task is to convert natural language instructions into detailed, executable browser automation steps.

Available Actions:
- navigate: Go to a specific URL
- click: Click on an element (button, link, etc.)
- type: Enter text into input fields
- select: Choose from dropdown menus
- scroll: Scroll the page up/down/to element
- wait: Wait for elements to load or conditions to be met
- screenshot: Take a screenshot for verification
- extract: Extract specific information from the page
- verify: Check if certain conditions are met

Element Targeting Methods:
- id: Element ID
- class: CSS class name
- xpath: XPath selector
- css: CSS selector
- text: Visible text content
- name: Element name attribute
- tag: HTML tag name

Response Format:
Return a JSON object with:
{
  "objective": "Clear description of what we're trying to achieve",
  "steps": [
    {
      "action": "action_name",
      "target": "element_selector_or_url",
      "value": "text_to_enter_or_option_to_select",
      "condition": "wait_condition_if_needed",
      "description": "Human readable description of this step"
    }
  ],
  "success_criteria": ["List of conditions that indicate task completion"],
  "estimated_time": estimated_seconds_to_complete
}

Important Guidelines:
1. Be specific with element selectors
2. Include wait conditions for dynamic content
3. Add verification steps to ensure actions succeeded
4. Handle potential errors and edge cases
5. Keep steps atomic and sequential
6. Use human-like interaction patterns
7. Always verify critical actions (like form submissions)

Example selectors:
- "id:search-button"
- "css:.submit-btn"
- "xpath://button[contains(text(), 'Submit')]"
- "text:Sign In"
- "class:nav-link"
"""
    
    async def process_prompt(self, user_prompt: str, context: Optional[Dict] = None) -> TaskPlan:
        """Process user prompt and return task plan"""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self._enhance_prompt(user_prompt, context)}
            ]
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.openai_client.chat.completions.create(
                    model=self.config.ai_model,
                    messages=messages,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
            
            content = response.choices[0].message.content
            task_data = json.loads(content)
            
            return self._parse_task_plan(task_data)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse AI response as JSON: {e}")
            raise ValueError("AI returned invalid JSON response")
        except Exception as e:
            self.logger.error(f"Error processing prompt: {e}")
            raise
    
    def _enhance_prompt(self, user_prompt: str, context: Optional[Dict] = None) -> str:
        """Enhance user prompt with context information"""
        enhanced = f"User Request: {user_prompt}\n\n"
        
        if context:
            if 'current_url' in context:
                enhanced += f"Current Page: {context['current_url']}\n"
            
            if 'page_title' in context:
                enhanced += f"Page Title: {context['page_title']}\n"
            
            if 'available_elements' in context:
                enhanced += f"Visible Elements: {context['available_elements']}\n"
            
            if 'previous_actions' in context:
                enhanced += f"Previous Actions: {context['previous_actions']}\n"
        
        enhanced += "\nPlease provide a detailed step-by-step plan to accomplish this task."
        
        return enhanced
    
    def _parse_task_plan(self, task_data: Dict) -> TaskPlan:
        """Parse task data into TaskPlan object"""
        steps = []
        for step_data in task_data.get('steps', []):
            step = TaskStep(
                action=step_data['action'],
                target=step_data.get('target'),
                value=step_data.get('value'),
                condition=step_data.get('condition'),
                description=step_data.get('description', '')
            )
            steps.append(step)
        
        return TaskPlan(
            objective=task_data['objective'],
            steps=steps,
            success_criteria=task_data.get('success_criteria', []),
            estimated_time=task_data.get('estimated_time', 0)
        )
    
    def analyze_page_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """Analyze page content to provide context for AI"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract key information
        title = soup.title.string if soup.title else "No title"
        
        # Find interactive elements
        interactive_elements = []
        for element in soup.find_all(['button', 'input', 'select', 'a', 'textarea']):
            element_info = {
                'tag': element.name,
                'text': element.get_text(strip=True)[:50],
                'id': element.get('id', ''),
                'class': ' '.join(element.get('class', [])),
                'type': element.get('type', ''),
                'href': element.get('href', '')
            }
            if any(element_info.values()):  # Only include if has meaningful attributes
                interactive_elements.append(element_info)
        
        # Find forms
        forms = []
        for form in soup.find_all('form'):
            form_info = {
                'action': form.get('action', ''),
                'method': form.get('method', 'GET'),
                'inputs': []
            }
            for inp in form.find_all(['input', 'select', 'textarea']):
                form_info['inputs'].append({
                    'name': inp.get('name', ''),
                    'type': inp.get('type', ''),
                    'placeholder': inp.get('placeholder', ''),
                    'required': inp.has_attr('required')
                })
            forms.append(form_info)
        
        return {
            'url': url,
            'title': title,
            'interactive_elements': interactive_elements[:20],  # Limit to first 20
            'forms': forms,
            'has_navigation': bool(soup.find_all(['nav', 'header'])),
            'has_search': bool(soup.find_all(['input'], {'type': 'search'})) or 
                         bool(soup.find_all(string=lambda text: text and 'search' in text.lower())),
        }
    
    def refine_plan(self, original_plan: TaskPlan, execution_context: Dict) -> TaskPlan:
        """Refine task plan based on execution results"""
        # This could be enhanced to use AI to adapt the plan based on results
        # For now, return the original plan
        return original_plan