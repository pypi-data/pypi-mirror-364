import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI
import anthropic
import google.generativeai as genai

from .config import Config
from .ai_processor import TaskStep, TaskPlan


class LLMProvider(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"


@dataclass
class LLMModel:
    provider: LLMProvider
    model_name: str
    display_name: str
    description: str
    max_tokens: int
    supports_functions: bool = True
    cost_per_1k_tokens: float = 0.0


class MultiLLMProcessor:
    """Enhanced AI processor supporting multiple LLM providers"""
    
    AVAILABLE_MODELS = [
        LLMModel(LLMProvider.OPENAI, "gpt-4", "GPT-4", "Most capable OpenAI model", 8192, True, 0.03),
        LLMModel(LLMProvider.OPENAI, "gpt-4-turbo", "GPT-4 Turbo", "Latest GPT-4 with higher context", 128000, True, 0.01),
        LLMModel(LLMProvider.OPENAI, "gpt-3.5-turbo", "GPT-3.5 Turbo", "Fast and efficient", 16385, True, 0.002),
        LLMModel(LLMProvider.CLAUDE, "claude-3-opus-20240229", "Claude 3 Opus", "Most powerful Claude model", 200000, False, 0.015),
        LLMModel(LLMProvider.CLAUDE, "claude-3-sonnet-20240229", "Claude 3 Sonnet", "Balanced performance", 200000, False, 0.003),
        LLMModel(LLMProvider.CLAUDE, "claude-3-haiku-20240307", "Claude 3 Haiku", "Fast and cost-effective", 200000, False, 0.00025),
        LLMModel(LLMProvider.GEMINI, "gemini-pro", "Gemini Pro", "Google's most capable model", 32000, False, 0.001),
        LLMModel(LLMProvider.GEMINI, "gemini-pro-vision", "Gemini Pro Vision", "Multimodal capabilities", 16000, False, 0.001),
    ]
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.current_provider = LLMProvider.OPENAI
        self.current_model = "gpt-3.5-turbo"
        
        # Initialize clients
        self.openai_client = None
        self.claude_client = None
        self.gemini_client = None
        
        self._initialize_clients()
        self.system_prompt = self._create_system_prompt()
    
    def _initialize_clients(self):
        """Initialize all LLM clients"""
        try:
            # OpenAI
            if self.config.openai_api_key:
                self.openai_client = OpenAI(api_key=self.config.openai_api_key)
                self.logger.info("OpenAI client initialized")
            
            # Claude/Anthropic
            if hasattr(self.config, 'claude_api_key') and self.config.claude_api_key:
                self.claude_client = anthropic.Anthropic(api_key=self.config.claude_api_key)
                self.logger.info("Claude client initialized")
            
            # Gemini
            if hasattr(self.config, 'gemini_api_key') and self.config.gemini_api_key:
                genai.configure(api_key=self.config.gemini_api_key)
                self.gemini_client = genai
                self.logger.info("Gemini client initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing LLM clients: {e}")
    
    def get_available_models(self) -> List[LLMModel]:
        """Get list of available models based on configured API keys"""
        available = []
        
        for model in self.AVAILABLE_MODELS:
            if model.provider == LLMProvider.OPENAI and self.openai_client:
                available.append(model)
            elif model.provider == LLMProvider.CLAUDE and self.claude_client:
                available.append(model)
            elif model.provider == LLMProvider.GEMINI and self.gemini_client:
                available.append(model)
        
        return available
    
    def set_model(self, provider: LLMProvider, model_name: str):
        """Set the current model to use"""
        self.current_provider = provider
        self.current_model = model_name
        self.logger.info(f"Switched to {provider.value}: {model_name}")
    
    def get_current_model(self) -> Optional[LLMModel]:
        """Get current model information"""
        for model in self.AVAILABLE_MODELS:
            if model.provider == self.current_provider and model.model_name == self.current_model:
                return model
        return None
    
    async def process_prompt(self, user_prompt: str, context: Optional[Dict] = None) -> TaskPlan:
        """Process user prompt using the current LLM"""
        try:
            enhanced_prompt = self._enhance_prompt(user_prompt, context)
            
            if self.current_provider == LLMProvider.OPENAI:
                response = await self._process_with_openai(enhanced_prompt)
            elif self.current_provider == LLMProvider.CLAUDE:
                response = await self._process_with_claude(enhanced_prompt)
            elif self.current_provider == LLMProvider.GEMINI:
                response = await self._process_with_gemini(enhanced_prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.current_provider}")
            
            return self._parse_task_plan(response)
            
        except Exception as e:
            self.logger.error(f"Error processing prompt with {self.current_provider.value}: {e}")
            raise
    
    async def _process_with_openai(self, prompt: str) -> Dict:
        """Process prompt with OpenAI"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.openai_client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    async def _process_with_claude(self, prompt: str) -> Dict:
        """Process prompt with Claude"""
        full_prompt = f"{self.system_prompt}\n\nHuman: {prompt}\n\nAssistant:"
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.claude_client.completions.create(
                model=self.current_model,
                prompt=full_prompt,
                max_tokens_to_sample=self.config.max_tokens,
                temperature=self.config.temperature
            )
        )
        
        content = response.completion.strip()
        return json.loads(content)
    
    async def _process_with_gemini(self, prompt: str) -> Dict:
        """Process prompt with Gemini"""
        model = self.gemini_client.GenerativeModel(self.current_model)
        
        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
        )
        
        content = response.text
        return json.loads(content)
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for task planning"""
        return """You are an intelligent automation agent capable of both web browser and desktop control. Convert natural language instructions into detailed, executable automation steps.

BROWSER AUTOMATION ACTIONS:
- navigate: Go to a specific URL
- click: Click on a web element (button, link, etc.)
- type: Enter text into web input fields
- select: Choose from web dropdown menus
- scroll: Scroll the webpage up/down/to element
- wait: Wait for web elements to load or conditions to be met
- screenshot: Take a screenshot of the browser
- extract: Extract specific information from the webpage
- verify: Check if certain web conditions are met

DESKTOP AUTOMATION ACTIONS:
- click_coordinates: Click at specific screen coordinates (x, y)
- click_image: Find and click an image on screen
- type: Type text using keyboard (works anywhere on desktop)
- press_key: Press specific keys or key combinations (ctrl+c, cmd+v, etc.)
- scroll: Scroll at current mouse position or specific coordinates
- drag_drop: Drag from one position to another
- open_app: Open a desktop application by name
- move_mouse: Move mouse to specific coordinates
- wait_for_image: Wait for an image to appear on screen
- get_mouse_position: Get current mouse coordinates
- get_screen_info: Get screen resolution and information

HYBRID AUTOMATION ACTIONS:
- browser_to_desktop: Perform browser action then desktop action
- desktop_to_browser: Perform desktop action then browser action
- copy_from_browser_to_desktop: Extract text from browser and type in desktop app

Element Targeting Methods (Browser):
- id: Element ID (id:search-button)
- class: CSS class name (class:submit-btn)
- xpath: XPath selector (xpath://button[text()='Submit'])
- css: CSS selector (css:.nav-link)
- text: Visible text content (text:Sign In)
- name: Element name attribute (name:username)

Response Format (JSON):
{
  "objective": "Clear description of what we're trying to achieve",
  "steps": [
    {
      "action": "action_name",
      "type": "browser|desktop|hybrid",
      "target": "element_selector_or_coordinates_or_image_path",
      "value": "text_to_enter_or_option_to_select",
      "condition": "wait_condition_if_needed",
      "description": "Human readable description of this step",
      "params": {
        "x": 100,
        "y": 200,
        "button": "left",
        "app_name": "Calculator",
        "key": "ctrl+c",
        "confidence": 0.8
      }
    }
  ],
  "success_criteria": ["List of conditions that indicate task completion"],
  "estimated_time": estimated_seconds_to_complete
}

Guidelines:
1. Determine if task requires browser, desktop, or hybrid automation
2. Use browser automation for web-based tasks
3. Use desktop automation for system-wide tasks, opening apps, file operations
4. Use hybrid automation when task spans both browser and desktop
5. Be specific with selectors and coordinates
6. Include wait conditions for dynamic content
7. Add verification steps to ensure actions succeeded
8. Handle potential errors and edge cases
9. Keep steps atomic and sequential
10. Use human-like interaction patterns"""
    
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
        
        enhanced += "\nPlease provide a detailed step-by-step plan to accomplish this task in JSON format."
        
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
                description=step_data.get('description', ''),
                automation_type=step_data.get('type', 'browser'),
                params=step_data.get('params', {})
            )
            steps.append(step)
        
        return TaskPlan(
            objective=task_data['objective'],
            steps=steps,
            success_criteria=task_data.get('success_criteria', []),
            estimated_time=task_data.get('estimated_time', 0)
        )
    
    async def generate_response(self, user_message: str, context: Optional[Dict] = None) -> str:
        """Generate a conversational response (not a task plan)"""
        try:
            prompt = f"Respond conversationally to this user message: {user_message}"
            
            if self.current_provider == LLMProvider.OPENAI:
                messages = [
                    {"role": "system", "content": "You are a helpful AI assistant for browser automation. Respond naturally and helpfully."},
                    {"role": "user", "content": prompt}
                ]
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.openai_client.chat.completions.create(
                        model=self.current_model,
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                )
                
                return response.choices[0].message.content
            
            elif self.current_provider == LLMProvider.CLAUDE:
                full_prompt = f"Human: {prompt}\n\nAssistant:"
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.claude_client.completions.create(
                        model=self.current_model,
                        prompt=full_prompt,
                        max_tokens_to_sample=500,
                        temperature=0.7
                    )
                )
                
                return response.completion.strip()
            
            elif self.current_provider == LLMProvider.GEMINI:
                model = self.gemini_client.GenerativeModel(self.current_model)
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: model.generate_content(prompt)
                )
                
                return response.text
                
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    async def analyze_page_content(self, html_content: str, url: str = "", task_context: Optional[str] = None) -> Dict[str, Any]:
        """Analyze page content and extract relevant information for automation"""
        try:
            prompt = f"""Analyze the following webpage content and extract information useful for browser automation.

URL: {url}
Task Context: {task_context or 'General analysis'}

HTML Content (truncated):
{html_content[:5000]}...

Please provide a JSON response with:
1. Available interactive elements (buttons, links, forms, inputs)
2. Key information on the page
3. Suggested automation actions
4. Element selectors for common actions

Response format:
{{
    "title": "page title",
    "interactive_elements": [
        {{"type": "button", "text": "button text", "selector": "css or xpath selector"}},
        {{"type": "input", "placeholder": "input placeholder", "selector": "selector"}},
        {{"type": "link", "text": "link text", "href": "url", "selector": "selector"}}
    ],
    "key_information": ["important info point 1", "info point 2"],
    "suggested_actions": ["action 1", "action 2"],
    "page_type": "search/form/product/article/etc"
}}"""

            if self.current_provider == LLMProvider.OPENAI:
                messages = [
                    {"role": "system", "content": "You are an expert at analyzing webpages for browser automation. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ]
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.openai_client.chat.completions.create(
                        model=self.current_model,
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.3
                    )
                )
                
                content = response.choices[0].message.content
                return json.loads(content)
            
            elif self.current_provider == LLMProvider.CLAUDE:
                full_prompt = f"Human: {prompt}\n\nAssistant:"
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.claude_client.completions.create(
                        model=self.current_model,
                        prompt=full_prompt,
                        max_tokens_to_sample=1000,
                        temperature=0.3
                    )
                )
                
                content = response.completion.strip()
                return json.loads(content)
            
            elif self.current_provider == LLMProvider.GEMINI:
                model = self.gemini_client.GenerativeModel(self.current_model)
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: model.generate_content(prompt)
                )
                
                content = response.text
                return json.loads(content)
                
        except Exception as e:
            self.logger.error(f"Error analyzing page content: {e}")
            return {
                "title": "Analysis Failed",
                "interactive_elements": [],
                "key_information": [f"Error analyzing page: {str(e)}"],
                "suggested_actions": [],
                "page_type": "unknown"
            }