from src.CrawlerProcess.DebugHTMLSaver.DebugHTMLSaver import DebugHTMLSaver
from pathlib import Path
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
from abc import ABC, abstractmethod

class AbstractURLProcessor(ABC):

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

    @abstractmethod
    def _process_url(self, source_id: str, url: str, level: int, page_type: str):
        """
        Process a single URL. This runs in a thread.
        Must use locks for all shared data structure access.
        """
        pass
    
    @abstractmethod
    def _manage_info(self, page_type, source_id, html, level, url):
        """
        Process page info according to the page type
        """
        pass