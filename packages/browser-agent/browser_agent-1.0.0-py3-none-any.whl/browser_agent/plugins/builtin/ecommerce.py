from typing import Dict, Any, List
from ..base import BasePlugin, PluginMetadata


class EcommercePlugin(BasePlugin):
    """Plugin for e-commerce automation tasks"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ecommerce",
            version="1.0.0",
            description="Handles e-commerce tasks like product search, cart management, and checkout",
            author="Browser Agent Team",
            category="ecommerce",
            supported_browsers=["chrome", "firefox", "edge"]
        )
    
    def can_handle(self, task_type: str, context: Dict[str, Any]) -> bool:
        """Check if this plugin can handle e-commerce tasks"""
        ecommerce_indicators = [
            "buy", "purchase", "add to cart", "checkout", "shop", "product",
            "amazon", "ebay", "shopping", "order", "price", "compare"
        ]
        
        task_lower = task_type.lower()
        return any(indicator in task_lower for indicator in ecommerce_indicators)
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute e-commerce task"""
        action = task_data.get('action', '').lower()
        
        if 'search' in action:
            return await self._search_product(task_data)
        elif 'add_to_cart' in action or 'add to cart' in action:
            return await self._add_to_cart(task_data)
        elif 'checkout' in action:
            return await self._checkout(task_data)
        elif 'compare' in action:
            return await self._compare_prices(task_data)
        else:
            return await self._generic_ecommerce_task(task_data)
    
    async def _search_product(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for a product"""
        try:
            search_term = task_data.get('product_name') or task_data.get('search_term')
            if not search_term:
                return {'success': False, 'error': 'No search term provided'}
            
            # Common search box selectors
            search_selectors = [
                "css:input[type='search']",
                "css:input[name*='search']",
                "css:input[id*='search']",
                "css:input[placeholder*='search']",
                "css:.search-input",
                "css:#search",
                "css:.search-box"
            ]
            
            search_element = None
            for selector in search_selectors:
                element = await self._automation._find_element(selector)
                if element:
                    search_element = selector
                    break
            
            if not search_element:
                return {'success': False, 'error': 'Search box not found'}
            
            # Type search term
            type_result = await self._automation.type_text(search_element, search_term)
            if not type_result.get('success'):
                return type_result
            
            # Submit search
            submit_result = await self._submit_search(search_element)
            
            # Extract search results
            results = await self._extract_search_results()
            
            return {
                'success': True,
                'search_term': search_term,
                'results_found': len(results),
                'results': results[:10]  # Limit to first 10 results
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _submit_search(self, search_selector: str) -> Dict[str, Any]:
        """Submit search form"""
        # Try Enter key first
        try:
            element = await self._automation._find_element(search_selector)
            if element:
                element.send_keys("\n")
                return {'success': True}
        except:
            pass
        
        # Try search button
        search_button_selectors = [
            "css:button[type='submit']",
            "css:input[type='submit']",
            "css:.search-button",
            "css:.search-btn",
            "text:Search"
        ]
        
        for selector in search_button_selectors:
            try:
                result = await self._automation.click_element(selector)
                if result.get('success'):
                    return result
            except:
                continue
        
        return {'success': False, 'error': 'Could not submit search'}
    
    async def _extract_search_results(self) -> List[Dict[str, Any]]:
        """Extract product search results"""
        results = []
        
        # Common product selectors
        product_selectors = [
            "css:.product",
            "css:.item",
            "css:[data-product]",
            "css:.search-result",
            "css:.product-item"
        ]
        
        for selector in product_selectors:
            try:
                elements = await self._automation._find_elements(selector)
                if elements:
                    for i, element in enumerate(elements[:10]):  # Limit to 10
                        try:
                            title = self._extract_text(element, ['.title', '.name', 'h2', 'h3'])
                            price = self._extract_text(element, ['.price', '.cost', '.amount'])
                            link = element.get_attribute('href') or self._extract_link(element)
                            
                            if title:
                                results.append({
                                    'title': title,
                                    'price': price,
                                    'link': link,
                                    'position': i + 1
                                })
                        except:
                            continue
                    break
            except:
                continue
        
        return results
    
    async def _add_to_cart(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add product to cart"""
        try:
            # Common add to cart button selectors
            cart_selectors = [
                "text:Add to Cart",
                "text:Add to Basket",
                "css:.add-to-cart",
                "css:.btn-cart",
                "css:button[name*='cart']",
                "css:input[value*='cart']"
            ]
            
            for selector in cart_selectors:
                try:
                    result = await self._automation.click_element(selector)
                    if result.get('success'):
                        return {
                            'success': True,
                            'message': 'Product added to cart',
                            'selector_used': selector
                        }
                except:
                    continue
            
            return {'success': False, 'error': 'Add to cart button not found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _checkout(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Proceed to checkout"""
        try:
            # Common checkout button selectors
            checkout_selectors = [
                "text:Checkout",
                "text:Proceed to Checkout",
                "css:.checkout",
                "css:.btn-checkout",
                "css:a[href*='checkout']"
            ]
            
            for selector in checkout_selectors:
                try:
                    result = await self._automation.click_element(selector)
                    if result.get('success'):
                        return {
                            'success': True,
                            'message': 'Proceeded to checkout',
                            'selector_used': selector
                        }
                except:
                    continue
            
            return {'success': False, 'error': 'Checkout button not found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _compare_prices(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare prices across different sites"""
        try:
            product_name = task_data.get('product_name')
            sites = task_data.get('sites', ['amazon.com', 'ebay.com'])
            
            if not product_name:
                return {'success': False, 'error': 'Product name required for price comparison'}
            
            price_data = []
            
            for site in sites:
                try:
                    # Navigate to site
                    await self._automation.navigate(f"https://{site}")
                    
                    # Search for product
                    search_result = await self._search_product({'product_name': product_name})
                    
                    if search_result.get('success') and search_result.get('results'):
                        best_result = search_result['results'][0]
                        price_data.append({
                            'site': site,
                            'product': best_result.get('title'),
                            'price': best_result.get('price'),
                            'link': best_result.get('link')
                        })
                except Exception as e:
                    price_data.append({
                        'site': site,
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'product_name': product_name,
                'price_comparison': price_data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _generic_ecommerce_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic e-commerce tasks"""
        return {
            'success': True,
            'message': 'Generic e-commerce task executed',
            'task_data': task_data
        }
    
    def _extract_text(self, element, selectors: List[str]) -> str:
        """Extract text from element using multiple selectors"""
        for selector in selectors:
            try:
                sub_element = element.find_element("css selector", selector)
                text = sub_element.text.strip()
                if text:
                    return text
            except:
                continue
        
        # Fallback to element's own text
        return element.text.strip()
    
    def _extract_link(self, element) -> str:
        """Extract link from element"""
        try:
            link_element = element.find_element("css selector", "a")
            return link_element.get_attribute('href')
        except:
            return ""
    
    def get_supported_actions(self) -> List[str]:
        """Return supported actions"""
        return [
            "search_product", "add_to_cart", "checkout", 
            "compare_prices", "view_product", "filter_results"
        ]