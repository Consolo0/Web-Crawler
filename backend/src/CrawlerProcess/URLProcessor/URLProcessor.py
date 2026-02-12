from src.Error.NoHTML import NoHTML
from src.CrawlerProcess.DebugHTMLSaver.DebugHTMLSaver import DebugHTMLSaver
from pathlib import Path
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
import traceback

class URLProcessor:

    def __init__(self, sources_rules, fetcher, url_visited, url_visited_lock, error_handler, error_lock, sources_and_types_visited, processor: AbstractListingProcessor, debug_mode=False):
        self.sources_rules = sources_rules
        self.fetcher = fetcher
        self.url_visited = url_visited
        self.url_visited_lock = url_visited_lock
        self.error_handler = error_handler
        self.error_lock = error_lock
        self.debug_mode = debug_mode
        self.sources_and_types_visited = sources_and_types_visited

        if self.debug_mode:
            debug_dir = Path("debug_html")
            debug_dir.mkdir(exist_ok=True)
            self.debug_html_saver = DebugHTMLSaver(debug_dir, self.url_visited_lock, self.error_lock, self.sources_and_types_visited)
        
        self.processor = processor

    def _process_url(self, source_id: str, url: str, level: int, page_type: str):
        """
        Process a single URL. This runs in a thread.
        Must use locks for all shared data structure access.
        """
        print(f"Procesando el url={url}")
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
        
        # Process based on page type
        if page_type in ("search", "category"):
            self.processor._process_listing_page_safe_and_save(source_id, html, level)
        
        elif page_type == "product":
            self.processor._process_product_page_safe_and_save(source_id, html, url)
