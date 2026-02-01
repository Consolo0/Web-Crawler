from collections import defaultdict
import traceback
from pathlib import Path
from bs4 import BeautifulSoup
from src.Error.NoHTML import NoHTML
from src.CrawlerProcess.CutEvaluator.CutEvaluator import CutEvaluator
from src.CrawlerProcess.Fetch.Fetcher import Fetcher
from src.CrawlerProcess.TextNormalizer.TextNormalizer import TextNormalizer
from src.Enums.InfoCategories import InfoCategories
from src.CrawlerProcess.ResultIntegrator.ResultIntegrator import ResultIntegrator
from src.CrawlerProcess.ListingProcessors.ListingProcessorFactory import ListingProcessorFactory
from src.CrawlerProcess.URLConverter import URLConverter

class Crawler:

    def __init__(self, navigator, sources_metadata, error_handler,
        page_visit_handler, price_handler, stop_criteria, debug_mode=False):

        self.navigator = navigator
        self.sources_rules = sources_metadata
        self.error_handler = error_handler
        self.page_visit_handler = page_visit_handler
        self.price_handler = price_handler
        self.cut_evaluator = CutEvaluator(stop_criteria)
        self.url_visited = set()
        self.fetcher = Fetcher()

        self.debug_mode = debug_mode
        if self.debug_mode:
            self.debug_dir = Path("debug_html")
            self.debug_dir.mkdir(exist_ok=True)
            self.sources_and_types_visited = set()
        self.results = ResultIntegrator()
        
        # Initialize the listing processors (JSON extraction for each website)
        ListingProcessorFactory.initialize_default_processors()
        self.processor_factory = ListingProcessorFactory()

    def crawl(self) -> ResultIntegrator:

        while not self.navigator.is_empty():

            if not self.cut_evaluator.should_continue(
                self.error_handler.get_length()
            ):
                break
    
            source_id, url, level, page_type = self.navigator.get_element()

            if url in self.url_visited:
                continue
            if self.debug_mode and (source_id, page_type) in self.sources_and_types_visited:
                continue

            source_ctx = self.sources_rules.get(source_id)

            if not source_ctx:
                continue

            try:
                html = self.fetcher.fetch(url, source_ctx["Source"]["RequireJS"])

                print(f"In the URL: {url} | Fetched HTML length: {len(html)}")
            
                if not html:
                    raise NoHTML(f"No HTML fetched for URL: {url}")

                # For debugging, save the HTML
                if self.debug_mode:
                    self._save_debug_html(source_id, html, page_type)
                    self.sources_and_types_visited.add((source_id, page_type))

            except Exception as e:
                traceback.print_exc()
                self.error_handler.add_element((source_id, url, e))
                continue

            self.url_visited.add(url) 

            if page_type in ("search", "category"):

                product_urls = self._process_listing_page(
                    source_id,
                    html,
                )

                for url in product_urls:
                    self.navigator.add(
                        source=source_id,
                        url=url,
                        level=level + 1,
                        page_type="product"
                    )

            elif page_type == "product":
                
                data = self._process_product_page(
                    source_id,
                    html,
                )

                self.results.add_result(source_id, url, data)
        return self.results
    
    def _save_debug_html(self, source_id, html, page_type):
        """Save HTML to a formatted file for debugging in debug_html/ folder at root"""
        try:
            filename = f"{source_id}_{page_type}.html"
            filepath = self.debug_dir / filename
            
            # Pretty print the HTML
            soup = BeautifulSoup(html, "html.parser")
            formatted_html = soup.prettify()
            
            filepath.write_text(formatted_html, encoding="utf-8")
            
        except Exception as e:
            traceback.print_exc()
    
    def _process_listing_page(self, source_id, html):
        """
        Process a listing page to extract product links.
        
        This now uses the factory pattern to get the appropriate processor:
        - If the source has a custom processor (JSON extraction), use it
        - Otherwise, fall back to CSS selectors
        """
        try:
            processor = self.processor_factory.get_processor(source_id)
            product_urls = processor.extract_product_urls(html)
            
            source_domain = self.sources_rules[source_id]["Source"]["Domain"]
            converter = URLConverter(source_domain)
            absolute_urls = converter.to_absolute(product_urls)
            
            return absolute_urls
        
        except Exception as e:
            traceback.print_exc()
            return []
    
    def _process_product_page(self, source_id, html):
        """
        Process a product page to extract product information.
        Expects html as a string, converts to BeautifulSoup for parsing.
        """
        
        extracted = {}
        
        try:
            processor = self.processor_factory.get_processor(source_id)
            extracted = processor.extract_product_info(html)

        except Exception as e:
            traceback.print_exc()
            
        return extracted


