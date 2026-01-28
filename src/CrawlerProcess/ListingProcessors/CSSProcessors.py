from typing import List
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor


class CSSListingProcessor(AbstractListingProcessor):
    """
    Fallback processor using CSS selectors.
    
    Used for websites without JSON data or when JSON extraction fails.
    This is the "old way" but still useful as a fallback.
    """
    
    def extract_product_urls(self, html_content: str, selector: str = "a") -> List[str]:
        """
        Extract product URLs using CSS selector.
        
        Args:
            html_content: HTML content (BeautifulSoup object)
            selector: CSS selector to find links
        """
        return self._extract_links_from_css(html_content, selector)
