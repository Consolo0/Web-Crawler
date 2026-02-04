import traceback
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from bs4 import BeautifulSoup
from src.Error.NoHTML import NoHTML
from src.CrawlerProcess.CutEvaluator.CutEvaluator import CutEvaluator
from src.CrawlerProcess.Fetch.Fetcher import Fetcher
from src.CrawlerProcess.ResultIntegrator.ResultIntegrator import ResultIntegrator
from src.CrawlerProcess.ListingProcessors.ListingProcessorFactory import ListingProcessorFactory
from src.CrawlerProcess.URLConverter import URLConverter

class Crawler:

    def __init__(self, navigator, sources_metadata, error_handler,
        page_visit_handler, price_handler, stop_criteria, navigation_strategy, debug_mode=False, num_threads=4):

        self.navigator = navigator
        self.sources_rules = sources_metadata
        self.error_handler = error_handler
        self.page_visit_handler = page_visit_handler
        self.price_handler = price_handler
        self.cut_evaluator = CutEvaluator(stop_criteria)
        self.navigation_strategy = navigation_strategy
        self.url_visited = set()
        self.fetcher = Fetcher()

        self.debug_mode = debug_mode
        if self.debug_mode:
            self.debug_dir = Path("debug_html")
            self.debug_dir.mkdir(exist_ok=True)
            self.sources_and_types_visited = set()

        self.results = ResultIntegrator()
        
        ListingProcessorFactory.initialize_default_processors(self.navigation_strategy)
        self.processor_factory = ListingProcessorFactory()
        
        self.num_threads = num_threads
        
        self.navigator_lock = threading.RLock()   
        self.url_visited_lock = threading.Lock()  
        self.visited_types_lock = threading.Lock()
        self.results_lock = threading.Lock()      
        self.error_lock = threading.Lock()        
        self.debug_lock = threading.Lock()        

    def crawl(self) -> ResultIntegrator:
        """
        Multi-threaded crawl using ThreadPoolExecutor.
        Each thread fetches and processes URLs independently.
        """

        print(f"Navigator: {self.navigator}")
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = set()
            
            while True:

                with self.error_lock:
                    if not self.cut_evaluator.should_continue(
                        self.error_handler.get_length()
                    ):
                        print("Cut criteria met, stopping crawl.")
                        break

                got_item = False
                with self.navigator_lock:

                    if not self.navigator.is_empty() and len(futures) < self.num_threads:
                        source_id, url, level, page_type = self.navigator.get_element()
                        got_item = True

                if got_item:

                    with self.url_visited_lock:
                        if url in self.url_visited:
                            print(f"URL already visited, skipping: {url}")
                            continue
                    
                    if self.debug_mode:
                        with self.visited_types_lock:
                            if (source_id, page_type) in self.sources_and_types_visited:
                                print(f"Debug mode: already visited source/type, skipping debug save: {source_id} | {page_type}")
                                continue
                    
                    future = executor.submit(
                        self._process_url,
                        source_id, url, level, page_type
                    )
                    futures.add(future)
                
                if not got_item and futures:
                    print(f"Navigator empty, waiting for {len(futures)} futures to complete...")
                    try:
                        for future in as_completed(futures, timeout=30):
                            try:
                                future.result()
                            except Exception as e:
                                traceback.print_exc()
                            finally:
                                futures.discard(future)
                            break
                    except TimeoutError:
                        pass
                    continue

                if not got_item and not futures:
                    print("Navigator is empty and no futures pending, stopping crawl.")
                    break
                
                if len(futures) >= self.num_threads * 2:
                    print(f"Too many futures ({len(futures)}), waiting for at least one to complete...")
                    try:
                        for future in as_completed(futures, timeout=30):
                            try:
                                future.result()
                            except Exception as e:
                                traceback.print_exc()
                            finally:
                                futures.discard(future)
                            break
                    except TimeoutError:
                        pass
            
            print(f"Main loop done, waiting for {len(futures)} remaining futures...")
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    traceback.print_exc()
                finally:
                    futures.discard(future)
        
        return self.results
    
    def _process_url(self, source_id: str, url: str, level: int, page_type: str):
        """
        Process a single URL. This runs in a thread.
        Must use locks for all shared data structure access.
        """
        source_ctx = self.sources_rules.get(source_id)
        
        if not source_ctx:
            return
        
        try:
            # Fetch HTML (thread-safe, each thread has its own session)
            html = self.fetcher.fetch(url, source_ctx["Source"]["RequireJS"])
            
            print(f"[Thread {threading.current_thread().name}] URL: {url} | HTML length: {len(html)}")
            
            if not html:
                raise NoHTML(f"No HTML fetched for URL: {url}")
            
            # Save debug HTML if enabled (with lock to prevent file conflicts)
            if self.debug_mode:
                self._save_debug_html_safe(source_id, html, page_type)
        
        except Exception as e:
            # Add to error handler (with lock)
            with self.error_lock:
                self.error_handler.add_element((source_id, url, e))
            traceback.print_exc()
            return
        
        # Mark as visited (with lock)
        with self.url_visited_lock:
            self.url_visited.add(url)
        
        # Process based on page type
        if page_type in ("search", "category"):
            self._process_listing_page_safe_and_save(source_id, html, url, level)
        
        elif page_type == "product":
            self._process_product_page_safe_and_save(source_id, html, url)
    
    
    def _save_debug_html_safe(self, source_id, html, page_type):
        """Thread-safe version of _save_debug_html with lock"""
        # Must use visited_types_lock, not debug_lock (consistent with main loop)
        with self.visited_types_lock:
            with self.debug_lock:  # Separate lock for file I/O
                self._save_debug_html(source_id, html, page_type)
            self.sources_and_types_visited.add((source_id, page_type))
    
    def _process_listing_page_safe_and_save(self, source_id, html, url, level):
        """Thread-safe wrapper for listing page processing and saving"""
        product_urls = self._process_listing_page(source_id, html)
        
        # Add product URLs to navigator (with lock)
        with self.navigator_lock:
            for product_url in product_urls:
                self.navigator.add(
                    source=source_id,
                    url=product_url,
                    level=level + 1,
                    page_type="product"
                )
    
    def _process_product_page_safe_and_save(self, source_id, html, url):
        """Thread-safe wrapper for product page processing"""
        data = self._process_product_page(source_id, html)
        
        # Add results to ResultIntegrator (with lock)
        with self.results_lock:
            self.results.add_result(source_id, url, data)
    
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
        extracted = {}  # Initialize to empty dict
        
        try:
            processor = self.processor_factory.get_processor(source_id)
            extracted = processor.extract_product_info(html)

        except Exception as e:
            traceback.print_exc()
            # extracted remains empty dict if exception occurs

        return extracted
