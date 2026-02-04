from typing import Dict
from src.Error.NoRelatedProcessor import NoRelatedProcessor
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
from src.CrawlerProcess.ListingProcessors.MercadoLibreProcessor import MercadoLibreProcessor
from src.CrawlerProcess.ListingProcessors.FalabellaProcessor import FalabellaProcessor
from src.CrawlerProcess.ListingProcessors.ParisProcessor import ParisProcessor


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
    def get_processor(cls, source_id: str) -> AbstractListingProcessor:
        """
        Get the processor for a source.
        If not found, return a default CSS selector processor.
        """
        if source_id in cls._processors:
            return cls._processors[source_id]
        
        raise NoRelatedProcessor(f"No processor for source: {source_id}")

    @classmethod
    def initialize_default_processors(cls, navigation_strategy, extraction_rules, nav_rules) -> None:
        """
        Initialize default processors for known sources.
        Call this once when your app starts.
        """
        cls.register_processor("MERCADOLIBRE", MercadoLibreProcessor(navigation_strategy, extraction_rules, nav_rules))
        cls.register_processor("FALABELLA", FalabellaProcessor(navigation_strategy, extraction_rules, nav_rules))
        cls.register_processor("PARIS", ParisProcessor(navigation_strategy, extraction_rules, nav_rules))