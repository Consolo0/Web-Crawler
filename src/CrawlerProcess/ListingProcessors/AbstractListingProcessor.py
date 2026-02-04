from abc import ABC, abstractmethod
from collections import defaultdict
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

    def __init__(self, navigation_strategy, sources_rules):
        self.navigation_strategy = navigation_strategy
        self.sources_rules = sources_rules
        self.products_counter_per_source = defaultdict(lambda : 0)

    @abstractmethod
    def extract_product_urls(self, source_id: str, html_content: str) -> List[str]:
        """
        Extract product URLs from the page.
        
        Args:
            html_content: The raw HTML from the page
            
        Returns:
            List of product URLs (full URLs or relative paths)
        """
        pass

    @abstractmethod
    def extract_product_info(self, html: str) -> Dict:
        """
        Extract product information from a product page.
        
        Args:
            html: The raw HTML content of the product page
            
        Returns:
            Dictionary with InfoType enum keys and extracted values
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
