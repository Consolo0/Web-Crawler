from typing import List
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor


class MercadoLibreProcessor(AbstractListingProcessor):
    """
    Processor for MercadoLibre listing pages.
    
    How it works:
    1. MercadoLibre embeds product data in a <script> tag as JSON
    2. The JSON contains: "results": ["MLC123", "MLC456", ...]
    3. We extract this JSON and build product URLs from the IDs
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from MercadoLibre listing page.
        """
        # Step 1: Extract the embedded JSON data
        # Pattern: melidata("add","event_data",{ ... })
        json_pattern = r'melidata\("add","event_data",(\{.*?\})\);'
        event_data = self._extract_json_from_html(html_content, json_pattern)
        
        if not event_data:
            if self.debug_mode:
                print("  ⚠ Could not find MercadoLibre event_data JSON")
            return []
        
        # Step 2: Extract product IDs from the results array
        product_ids = event_data.get("results", [])
        
        if self.debug_mode:
            print(f"  ✓ Found {len(product_ids)} products via JSON extraction")
        
        # Step 3: Build product URLs from IDs
        # Format: https://listado.mercadolibre.cl/[ITEM_ID]-...
        # But we only need the ID part for now
        urls = [f"https://listado.mercadolibre.cl/{item_id}" for item_id in product_ids if item_id]
        
        return urls
