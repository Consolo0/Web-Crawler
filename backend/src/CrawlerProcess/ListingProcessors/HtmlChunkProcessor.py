from typing import Dict
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
from typing import List
import traceback

class HtmlChunkProcessor(AbstractListingProcessor):
    """
    Processor for search listings and extract the products html chunks for a more efficient search.

    No need to visit individual product pages.
    """
    def __init__(self, navigation_strategy, sources_rules, results, results_lock) -> None:
        super().__init__(navigation_strategy, sources_rules, results, results_lock)
    
    def _process_listing_page_safe_and_save(self, source_id, html, level):
        data = self._process_listing_page(source_id, html)

        with self.results_lock:
            self.results.add_results(source_id, level, data)

    def _process_listing_page(self, source_id, html):
        """
        Process a listing page to extract product links.
        
        This now uses the factory pattern to get the appropriate processor:
        - If the source has a custom processor (JSON extraction), use it
        - Otherwise, fall back to CSS selectors
        """
        try:
            return self.extract_product_info(source_id, html)
        
        except Exception as e:
            traceback.print_exc()
            return []
    
    def extract_product_info(self, source_id: str, html: str) -> Dict:
        """
        Extract raw HTML chunks of each product card from the listing page.
        Returns a list of HTML strings, one for each product.
        """
        if not html:
            return {}
    
        soup = BeautifulSoup(html, "html.parser")
        html_chunks = {}
        
        extraction_rules = self.sources_rules[source_id].get("ExtractionRules")
        card_selector = extraction_rules.get("ProductChunk", {})
        
        remaining_slots = self.navigation_strategy.maximun_products_per_source - self.products_counter_per_source[source_id]
        product_cards = soup.select(card_selector, limit=remaining_slots)
        
        for i, card in enumerate(product_cards):
            html_string = str(card)  # This gives you the full HTML of that element
            html_chunks[f"product_{i}"] = html_string
        
        self.products_counter_per_source[source_id] += len(html_chunks)
        return html_chunks
    
    def _process_product_page_safe_and_save(self, source_id, html, url):
        """Thread-safe wrapper for product page processing"""
        pass
    
    def _process_product_page(self, source_id, html):
        """
        Process a product page to extract product information.
        Expects html as a string, converts to BeautifulSoup for parsing.
        """
        pass
        
    def extract_product_urls(self, source_id: str, html_content: str) -> List[str]:
        """
        Extract product URLs from Page listing pages.
        
        Looks for <a id="product-*"> tags which contain product URLs.
        """
        if not html_content or self.navigation_strategy.maximun_products_per_source - self.products_counter_per_source[source_id] <= 0:
            return []
        
        soup = BeautifulSoup(html_content, "html.parser")
        urls = []
        nav_rules = self.sources_rules[source_id].get("NavRules")
        rules = nav_rules.get("search", {})
        selectors = rules.get("Selectors", "")
        attribute = rules.get("Link", "href")
        
        # Find all product links by id pattern: id="product-..."
        remaining_slots = self.navigation_strategy.maximun_products_per_source - self.products_counter_per_source[source_id]
        product_links = soup.select(f'{selectors}', limit=remaining_slots)
        self.products_counter_per_source[source_id] += len(product_links)
        
        for link in product_links:
            href = link.get(attribute)
            if href:
                urls.append(href)
        
        return urls
