from typing import List
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
import traceback


class RipleyProcessor(AbstractListingProcessor):
    """
    Processor for Ripley search listings.
    
    Ripley uses React with dynamic content loading.
    Looks for product containers and extracts URLs from links.
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from Ripley listing pages.
        
        Args:
            html_content: HTML content of the listing page
            
        Returns:
            List of product URLs
        """
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, "html.parser")
        urls = []
        
        # Ripley product URLs follow pattern: /p/productname-productid
        # Look for all links that match Ripley's product URL pattern
        selectors = [
            'a[href*="/p/"]',              # Product link pattern: /p/name-id
            'a.product-link',
            'a.item-link',
            'div.catalog-product-item a',
            'div[class*="product"] a[href*="ripley"]',
        ]
        
        for selector in selectors:
            try:
                links = soup.select(selector)
                for link in links:
                    href = link.get("href")
                    if href and "/p/" in href:
                        # Ensure absolute URL
                        if not href.startswith("http"):
                            if href.startswith("/"):
                                href = "https://simple.ripley.cl" + href
                            else:
                                href = "https://simple.ripley.cl/" + href
                        
                        # Avoid duplicates
                        if href not in urls and "ripley.cl" in href:
                            urls.append(href)
            except Exception as e:
                traceback.print_exc()
                continue
        
        return urls[:100]  # Limit to 100 products per page
