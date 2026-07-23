from src.CrawlerProcess.URLProcessor.AbstractUrlProcessor import AbstractURLProcessor
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
from src.Error.NoHTML import NoHTML
from src.Enums.PageStatus import PageStatus
import traceback

class StreamingURLProcessor(AbstractURLProcessor):

    def __init__(self, sources_rules, fetcher, url_visited, url_visited_lock, error_handler, error_lock, sources_and_types_visited, processor: AbstractListingProcessor, debug_mode=False):
        super().__init__(sources_rules, fetcher, url_visited, url_visited_lock, error_handler, error_lock, sources_and_types_visited, processor, debug_mode)

    def _process_url(self, source_id: str, url: str, level: int, page_type: str):
        """
        Process a single URL and yield results.
        This is a generator that yields results as they're produced.
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
        
        # Yield results from _manage_info
        yield from self._manage_info(page_type, source_id, html, level, url)

    def _manage_info(self, page_type, source_id, html, level, url):
        """
        Process page and yield results incrementally for streaming.
        Calls processing methods directly (not the save versions) and yields data.
        """
        # Process based on page type
        if page_type in ("search", "category"):
            # Call the processing method directly (not the save version)
            data = self.processor._process_listing_page(source_id, html)

            success = "products" in data
            missing = data == {}

            if success:
                data["status"] = PageStatus.SUCCESS.value
            elif missing:
                data["status"] = PageStatus.MISSING.value
            else:
                data["status"] = PageStatus.FAILED.value
            
            yield {
                "type": "listing_result",
                "source_id": source_id,
                "level": level,
                "url": url,
                "data": data,
                "products_count": len(data.get("products", {})) if success else 0
            }
        
        elif page_type == "product":
            # Call the processing method directly (not the save version)
            data = self.processor._process_product_page(source_id, html)
            
            if data:
                # Yield with metadata
                yield {
                    "type": "product_result",
                    "source_id": source_id,
                    "url": url,
                    "data": data
                }