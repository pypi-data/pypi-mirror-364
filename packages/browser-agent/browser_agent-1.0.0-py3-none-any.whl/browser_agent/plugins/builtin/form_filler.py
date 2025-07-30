from typing import Dict, Any, List
from ..base import BasePlugin, PluginMetadata


class FormFillerPlugin(BasePlugin):
    """Plugin for intelligent form filling"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="form_filler",
            version="1.0.0",
            description="Automatically fills out web forms with provided data",
            author="Browser Agent Team",
            category="automation",
            supported_browsers=["chrome", "firefox", "edge"]
        )
    
    def can_handle(self, task_type: str, context: Dict[str, Any]) -> bool:
        """Check if this plugin can handle form filling tasks"""
        form_indicators = [
            "fill form", "submit form", "enter data", "complete form",
            "registration", "signup", "login", "contact form"
        ]
        
        task_lower = task_type.lower()
        return any(indicator in task_lower for indicator in form_indicators)
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute form filling task"""
        try:
            form_data = task_data.get('form_data', {})
            form_selector = task_data.get('form_selector', 'form')
            submit_after = task_data.get('submit_after', True)
            
            if not form_data:
                return {
                    'success': False,
                    'error': 'No form data provided'
                }
            
            # Find the form
            form_element = await self._automation._find_element(form_selector)
            if not form_element:
                return {
                    'success': False,
                    'error': f'Form not found with selector: {form_selector}'
                }
            
            filled_fields = []
            errors = []
            
            # Fill each field
            for field_name, field_value in form_data.items():
                try:
                    field_result = await self._fill_field(field_name, field_value)
                    if field_result['success']:
                        filled_fields.append(field_name)
                    else:
                        errors.append(f"{field_name}: {field_result.get('error', 'Unknown error')}")
                except Exception as e:
                    errors.append(f"{field_name}: {str(e)}")
            
            # Submit form if requested
            submit_result = None
            if submit_after:
                submit_result = await self._submit_form(form_selector)
            
            return {
                'success': len(errors) == 0,
                'filled_fields': filled_fields,
                'errors': errors,
                'submitted': submit_result.get('success', False) if submit_result else False
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _fill_field(self, field_name: str, field_value: str) -> Dict[str, Any]:
        """Fill a specific form field"""
        # Try different selectors for the field
        selectors = [
            f"name:{field_name}",
            f"id:{field_name}",
            f"css:input[name='{field_name}']",
            f"css:input[id='{field_name}']",
            f"css:select[name='{field_name}']",
            f"css:textarea[name='{field_name}']",
            f"xpath://input[@placeholder='{field_name}']",
            f"xpath://label[contains(text(), '{field_name}')]/following-sibling::input"
        ]
        
        for selector in selectors:
            try:
                element = await self._automation._find_element(selector)
                if element:
                    # Determine field type and fill accordingly
                    field_type = element.get_attribute('type') or 'text'
                    tag_name = element.tag_name.lower()
                    
                    if tag_name == 'select':
                        return await self._automation.select_option(selector, field_value)
                    elif field_type in ['checkbox', 'radio']:
                        if field_value.lower() in ['true', '1', 'yes', 'on']:
                            return await self._automation.click_element(selector)
                        else:
                            return {'success': True, 'skipped': 'unchecked'}
                    else:
                        return await self._automation.type_text(selector, field_value)
            except:
                continue
        
        return {
            'success': False,
            'error': f'Field {field_name} not found'
        }
    
    async def _submit_form(self, form_selector: str) -> Dict[str, Any]:
        """Submit the form"""
        # Try different submit methods
        submit_selectors = [
            f"{form_selector} input[type='submit']",
            f"{form_selector} button[type='submit']",
            f"{form_selector} button",
            "css:input[type='submit']",
            "css:button[type='submit']",
            "text:Submit",
            "text:Send",
            "text:Continue"
        ]
        
        for selector in submit_selectors:
            try:
                element = await self._automation._find_element(selector)
                if element:
                    return await self._automation.click_element(selector)
            except:
                continue
        
        return {
            'success': False,
            'error': 'Submit button not found'
        }
    
    def get_supported_actions(self) -> List[str]:
        """Return supported actions"""
        return ["fill_form", "submit_form", "fill_field"]