from typing import Dict
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor

class HtmLChunkProcessor(AbstractListingProcessor):
    """
    Processor for search listings and extract the products html chunks for a more efficient search.

    No need to visit individual product pages.
    """
    def __init__(self, navigation_strategy, sources_rules) -> None:
        super().__init__(navigation_strategy, sources_rules)

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
