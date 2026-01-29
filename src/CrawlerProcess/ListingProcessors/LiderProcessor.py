from typing import List
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
import traceback

class LiderProcessor(AbstractListingProcessor):
    """
    Processor for LIDER (Walmart Chile) product listings.
    
    LIDER has strong anti-bot protection (Walmart's protection).
    This processor attempts to:
    1. Extract JSON data if available
    2. Fall back to CSS selectors for product links
    
    IMPORTANT: LIDER actively blocks bots. If you see "Robot or human?" pages,
    the site is detecting automated access.
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from LIDER listing pages.
        
        Args:
            html_content: HTML content of the listing page
            
        Returns:
            List of product URLs
        """
        
        # Try multiple approaches in order of preference
        urls = []
        
        # Approach 1: Look for JSON data in window.__INITIAL_STATE__ (common pattern)
        urls = self._extract_from_initial_state(html_content)
        if urls:
            return urls
        
        # Approach 2: Look for other JSON patterns
        urls = self._extract_from_json_script(html_content)
        if urls:
            return urls
        
        # Approach 3: Fall back to CSS selectors
        urls = self._extract_from_css_selectors(html_content)
        if urls:
            return urls
        
        return []
    
    def _extract_from_initial_state(self, html_content: str) -> List[str]:
        """Extract URLs from window.__INITIAL_STATE__ pattern"""
        import re
        import json
        
        # Look for window.__INITIAL_STATE__ = {...}
        pattern = r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            return []
        
        try:
            data = json.loads(match.group(1))
            
            # Navigate through common LIDER structure
            # Adjust these paths based on actual LIDER data structure
            products = data.get("products", {}).get("items", [])
            
            urls = []
            for product in products:
                if isinstance(product, dict):
                    # LIDER uses 'url' or 'href' for product links
                    url = product.get("url") or product.get("href") or product.get("link")
                    if url:
                        urls.append(url)
            
            return urls
        except Exception as e:
            traceback.print_exc()
            return []
    
    def _extract_from_json_script(self, html_content: str) -> List[str]:
        """Extract URLs from other JSON patterns"""
        import re
        import json
        
        # Look for various JSON patterns in script tags
        patterns = [
            r'var\s+products\s*=\s*(\[.*?\]);',
            r'var\s+items\s*=\s*(\[.*?\]);',
            r'"products"\s*:\s*(\[.*?\])',
            r'"items"\s*:\s*(\[.*?\])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    urls = []
                    for product in data:
                        if isinstance(product, dict):
                            url = product.get("url") or product.get("href") or product.get("link")
                            if url:
                                urls.append(url)
                    if urls:
                        return urls
                except:
                    continue
        
        return []
    
    def _extract_from_css_selectors(self, html_content: str) -> List[str]:
        """Fall back to CSS selectors"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Try multiple CSS selectors that commonly appear on LIDER
        selectors = [
            "a[href*='/producto/']",  # LIDER product pattern
            "a[href*='productid=']",
            "a.product-link",
            "a.item-link",
            "div.product a",
            "li.product a",
        ]
        
        for selector in selectors:
            try:
                links = soup.select(selector)
                urls = []
                for link in links:
                    href = link.get("href")
                    if href:
                        # Convert relative URLs to absolute if needed
                        if href.startswith("/"):
                            href = "https://lider.cl" + href
                        elif not href.startswith("http"):
                            href = "https://lider.cl/" + href
                        urls.append(href)
                
                if urls:
                    return urls
            except:
                continue
        
        return []
