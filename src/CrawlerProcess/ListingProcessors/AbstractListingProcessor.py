from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import json
import re
import traceback

class AbstractListingProcessor(ABC):
    """
    Base class for extracting product links from listing pages.
    
    Each website (MercadoLibre, Falabella, etc.) has a different structure,
    so we create a specific processor for each one.
    """

    @abstractmethod
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from the page.
        
        Args:
            html_content: The raw HTML from the page
            
        Returns:
            List of product URLs (full URLs or relative paths)
        """
        pass
    
    def _extract_json_from_html(self, html_text: str, pattern: str) -> Optional[Dict]:
        """
        Helper: Extract JSON data from HTML using regex pattern.
        
        This is the KEY to extracting data from modern websites!
        Most sites embed data as JSON in <script> tags.
        
        Args:
            html_text: Raw HTML content
            pattern: Regex pattern to find the JSON
            
        Returns:
            Parsed JSON as dictionary, or None if not found
        """
        try:
            match = re.search(pattern, str(html_text), re.DOTALL)
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            traceback.print_exc()
        return None
    
    def _extract_links_from_css(self, html_soup, selectors: str) -> List[str]:
        """
        Helper: Extract links using CSS selectors (fallback method).
        
        Args:
            html_soup: BeautifulSoup object
            selectors: CSS selector string
            
        Returns:
            List of href values
        """
        links = []
        try:
            elements = html_soup.select(selectors)
            for element in elements:
                href = element.get("href")
                if href:
                    links.append(href)
        except Exception as e:
            traceback.print_exc()

        return links
