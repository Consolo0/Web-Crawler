from src.Error.NoHTML import NoHTML
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
import traceback
from src.CrawlerProcess.URLProcessor.AbstractUrlProcessor import AbstractURLProcessor

class URLProcessor(AbstractURLProcessor):

    def __init__(self, sources_rules, fetcher, url_visited, url_visited_lock, error_handler, error_lock, sources_and_types_visited, processor: AbstractListingProcessor, debug_mode=False):
        super().__init__(sources_rules, fetcher, url_visited, url_visited_lock, error_handler, error_lock, sources_and_types_visited, processor, debug_mode)

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
            
            if not html:
                raise NoHTML(f"No HTML fetched for URL: {url}")
            
            # Save debug HTML if enabled (with lock to prevent file conflicts)
            if self.debug_mode:
                self.debug_html_saver._save_debug_html_safe(source_id, html, page_type)
        
        except Exception as e:
            # Add to error handler (with lock)
            with self.error_lock:
                self.error_handler.add_element((source_id, url, e))
            traceback.print_exc()
            return
        
        # Mark as visited (with lock)
        with self.url_visited_lock:
            self.url_visited.add(url)
        
        self._manage_info(page_type, source_id, html, level, url)
    
    def _manage_info(self, page_type, source_id, html, level, url):
        # Process based on page type
        if page_type in ("search", "category"):
            self.processor._process_listing_page_safe_and_save(source_id, html, level, url)
        
        elif page_type == "product":
            self.processor._process_product_page_safe_and_save(source_id, html, url)        
