from typing import List
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor


class FalabellaProcessor(AbstractListingProcessor):
    """
    Processor for Falabella listing pages.
    
    How it works:
    1. Falabella embeds data in window.__INITIAL_STATE__ as JSON
    2. Different structure than MercadoLibre, but same principle
    3. We find the products array and extract links
    
    NOTE: This is an EXAMPLE - you need to inspect Falabella's actual structure
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from Falabella listing page.
        """
        # Try to find Falabella's initial state JSON
        # Pattern might be: window.__INITIAL_STATE__ = { ... }
        json_pattern = r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});'
        initial_state = self._extract_json_from_html(html_content, json_pattern)
        
        if not initial_state:
            if self.debug_mode:
                print("  ⚠ Could not find Falabella __INITIAL_STATE__")
            return []
        
        urls = []
        try:
            # Navigate the Falabella JSON structure
            # (This structure would need to be inspected on actual Falabella site)
            products = initial_state.get("products", {}).get("items", [])
            
            for product in products:
                url = product.get("url")
                if url:
                    urls.append(url)
            
            if self.debug_mode:
                print(f"  ✓ Found {len(urls)} products via JSON extraction")
        
        except Exception as e:
            if self.debug_mode:
                print(f"  ⚠ Error processing Falabella data: {e}")
        
        return urls
