from typing import Dict
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
from src.CrawlerProcess.ListingProcessors.MercadoLibreProcessor import MercadoLibreProcessor
from src.CrawlerProcess.ListingProcessors.FalabellaProcessor import FalabellaProcessor


class ListingProcessorFactory:
    """
    Factory pattern: Creates the right processor based on the source.
    
    This is the KEY to making the system extendible!
    
    When you want to add a new website:
    1. Create a new processor class (e.g., ParisProcessor)
    2. Add it to the _processors dictionary
    3. That's it! No changes to Crawler.py needed
    """
    
    # Registry of available processors
    _processors: Dict[str, AbstractListingProcessor] = {}
    
    @classmethod
    def register_processor(cls, source_id: str, processor: AbstractListingProcessor):
        """
        Register a new processor for a source.
        
        Usage:
            factory = ListingProcessorFactory()
            factory.register_processor("PARIS", ParisProcessor())
        """
        cls._processors[source_id] = processor
    
    @classmethod
    def get_processor(cls, source_id: str, debug_mode: bool = False) -> AbstractListingProcessor:
        """
        Get the processor for a source.
        If not found, return a default CSS selector processor.
        """
        if source_id in cls._processors:
            return cls._processors[source_id]
        
        # Default: return a generic CSS selector processor
        from src.CrawlerProcess.ListingProcessors.CSSProcessors import CSSListingProcessor
        return CSSListingProcessor(debug_mode=debug_mode)
    
    @classmethod
    def initialize_default_processors(cls, debug_mode: bool = False):
        """
        Initialize default processors for known sources.
        Call this once when your app starts.
        """
        cls.register_processor("MERCADOLIBRE", MercadoLibreProcessor(debug_mode=debug_mode))
        cls.register_processor("FALABELLA", FalabellaProcessor(debug_mode=debug_mode))
        # Add more here as needed:
        # cls.register_processor("PARIS", ParisProcessor(debug_mode=debug_mode))
        # cls.register_processor("RIPLEY", RipleyProcessor(debug_mode=debug_mode))
