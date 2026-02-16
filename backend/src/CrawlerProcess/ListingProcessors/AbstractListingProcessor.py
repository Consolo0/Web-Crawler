from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Dict, Optional
import threading

class AbstractListingProcessor(ABC):
    """
    Base class for extracting product links from listing pages.
    
    Each website (MercadoLibre, Falabella, etc.) has a different structure,
    so we create a specific processor for each one.
    """

    def __init__(self, navigation_strategy, sources_rules, results, results_lock) -> None:
        self.navigation_strategy = navigation_strategy
        self.sources_rules = sources_rules
        self.results = results
        self.results_lock = results_lock
        self.products_counter_per_source = defaultdict(lambda : 0)
        self.products_counter_per_source_lock = threading.Lock()

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

    def _process_listing_page_safe_and_save(self, source_id, html, level, url) -> Dict:
        """Thread-safe wrapper for listing page processing and saving"""
        pass

    def _process_listing_page(self, source_id, html):
        """
        Process a listing page to extract product links.
        
        This now uses the factory pattern to get the appropriate processor:
        - If the source has a custom processor (JSON extraction), use it
        - Otherwise, fall back to CSS selectors
        """
        pass

    def _process_product_page_safe_and_save(self, source_id, html, url) -> Dict:
        """Thread-safe wrapper for product page processing"""
        pass

    def _process_product_page(self, source_id, html):
        """
        Process a product page to extract product information.
        Expects html as a string, converts to BeautifulSoup for parsing.
        """
        pass
