import traceback
from typing import List
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor


class ParisProcessor(AbstractListingProcessor):
    """
    Processor for Paris.cl search listings.
    
    Paris uses Chakra UI with dynamic product loading.
    Looks for product links in the page structure.
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from Paris listing pages.
        
        Args:
            html_content: HTML content of the listing page
            
        Returns:
            List of product URLs
        """
        from bs4 import BeautifulSoup
        
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, "html.parser")
        urls = []
        
        # Paris product URLs follow pattern: /producto/
        selectors = [
            'a[href*="/producto/"]',       # Main product pattern
            'a[href*="paris.cl/producto"]',
            'a.product-link',
            'a[data-testid*="product"]',
            'div[class*="product"] a[href]',
        ]
        
        for selector in selectors:
            try:
                links = soup.select(selector)
                for link in links:
                    href = link.get("href")
                    if href and ("producto" in href or "product" in href.lower()):
                        # Ensure absolute URL
                        if not href.startswith("http"):
                            if href.startswith("/"):
                                href = "https://paris.cl" + href
                            else:
                                href = "https://paris.cl/" + href
                        
                        # Avoid duplicates
                        if href not in urls and "paris.cl" in href:
                            urls.append(href)
            except Exception as e:
                traceback.print_exc()
                continue
        
        return urls[:100]  # Limit to 100 products per page
