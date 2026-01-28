from collections import defaultdict
import re
from pathlib import Path
from bs4 import BeautifulSoup
from src.CrawlerProcess.CutEvaluator.CutEvaluator import CutEvaluator
from src.CrawlerProcess.Fetch.Fetcher import Fetcher
from src.CrawlerProcess.TextNormalizer.TextNormalizer import TextNormalizer
from src.Enums.InfoCategories import InfoCategories
from src.CrawlerProcess.ResultIntegrator.ResultIntegrator import ResultIntegrator
from src.CrawlerProcess.ListingProcessors.ListingProcessorFactory import ListingProcessorFactory

class Crawler:

    def __init__(self, navigator, sources_metadata, error_handler,
        page_visit_handler, price_handler, stop_criteria, debug_mode=False, debug_dir="debug_html"):

        self.navigator = navigator
        self.sources_rules = sources_metadata
        self.error_handler = error_handler
        self.page_visit_handler = page_visit_handler
        self.price_handler = price_handler
        self.cut_evaluator = CutEvaluator(stop_criteria)
        self.url_visited = set()
        self.fetcher = Fetcher()
        self.debug_mode = debug_mode
        self.debug_dir = Path(debug_dir)
        
        if self.debug_mode:
            self.debug_dir.mkdir(parents=True, exist_ok=True)

        self.results = ResultIntegrator()
        
        # Initialize the listing processors (JSON extraction for each website)
        ListingProcessorFactory.initialize_default_processors(debug_mode=debug_mode)
        self.processor_factory = ListingProcessorFactory()

    def crawl(self) -> ResultIntegrator:
        contador = 0
        while not self.navigator.is_empty():
            source_id, url, level, page_type = self.navigator.get_element()

            if url in self.url_visited:
                continue
            source_ctx = self.sources_rules.get(source_id)

            if not source_ctx:
                continue

            """if not self._is_url_allowed(url, source_ctx["ValidationRules"]):
                continue"""
        
            try:
                html = self.fetcher.fetch(url, source_ctx["Source"]["RequireJS"])
                
                if self.debug_mode:
                    self._save_debug_html(source_id, url, html, page_type)
                
                if contador == 0:
                    print(f"HTML saved to debug folder. Check {self.debug_dir} for formatted HTML files.")
                    contador += 1
                    if self.debug_mode:
                        return {}

            except Exception as e:
                self.error_handler.add_element((source_id, url, e))
                continue
            
            if not html:
                continue
            self.url_visited.add(url) 

            if page_type in ("search", "category"):

                self._process_listing_page(
                    source_id,
                    html,
                    source_ctx["NavRules"],
                    level
                )

            elif page_type == "product":

                data = self._process_product_page(
                    html,
                    source_ctx["ExtractionRules"]
                )

                self.results.add_result(source_id, url, data)
            
            if not self.cut_evaluator.should_continue(
                self.error_handler.add_element((source_id, url, "Cut criteria met"))
            ):
                break
        
        return self.results

    def _is_url_allowed(self, url, validation_rules):
        for rule in validation_rules:
            for pattern in rule.get("AllowedPaths", []):
                if re.search(pattern, url):
                    return True
        return False
    
    def _save_debug_html(self, source_id, url, html, page_type):
        """Save HTML to a formatted file for debugging"""
        try:
            filename = f"{source_id}_{page_type}.html"
            filepath = self.debug_dir / filename
            
            # Pretty print the HTML
            soup = BeautifulSoup(str(html), "html.parser")
            formatted_html = soup.prettify()
            
            filepath.write_text(formatted_html, encoding="utf-8")
            print(f"✓ Saved: {filepath}")
            print(f"  URL: {url}")
            
        except Exception as e:
            print(f"Error saving debug HTML: {e}")
    
    def _process_listing_page(self, source_id, html, nav_rules, level):
        """
        Process a listing page to extract product links.
        
        This now uses the factory pattern to get the appropriate processor:
        - If the source has a custom processor (JSON extraction), use it
        - Otherwise, fall back to CSS selectors
        """
        # Get the processor for this source
        processor = self.processor_factory.get_processor(source_id, debug_mode=self.debug_mode)
        
        # Extract product URLs
        product_urls = processor.extract_product_urls(html)
        
        if not product_urls and self.debug_mode:
            print(f"  ⚠ No products extracted from {source_id}")
        
        # Add each product URL to the crawler queue
        for url in product_urls:
            self.navigator.add_element(
                source_id=source_id,
                url=url,
                level=level + 1,
                page_type="product"
            )
    
    def _process_product_page(self, html, extraction_rules):
        extracted = {}

        rules_by_entity = defaultdict(list)
        for rule in extraction_rules:
            rules_by_entity[rule["Type"]].append(rule)

        for entity, rules in rules_by_entity.items():
            rules.sort(key=lambda r: r.get("Priority", 1))

            for rule in rules:
                selector = rule["Selector"]
                attr = rule["Attribute"]

                nodes = html.select(selector)
                
                if self.debug_mode and not nodes:
                    print(f"  ⚠ Selector failed for {entity}: '{selector}'")
                
                if not nodes:
                    continue

                if attr == "text":
                    value = nodes[0].get_text(strip=True)
                elif attr == "existence":
                    value = True
                else:
                    value = nodes[0].get(attr)

                if value:
                    extracted[entity] = value
                    if self.debug_mode:
                        print(f"  ✓ Found {entity}: {value[:50]}...")
                    break
        
        for key in InfoCategories.NumberCategory:
            numberInfoType = key.value
            extracted[numberInfoType] = TextNormalizer.normalize(
                extracted[numberInfoType]
            )
            
        return extracted


