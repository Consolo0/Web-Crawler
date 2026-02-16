from src.CrawlerProcess.ResultIntegrator.ResultIntegrator import ResultIntegrator
from src.Enums.ProcessorType import ProcessorType
from pathlib import Path
from src.CrawlerProcess.CutEvaluator.CutEvaluator import CutEvaluator
from src.CrawlerProcess.Fetch.Fetcher import Fetcher
from src.CrawlerProcess.ListingProcessors.ProcessorFactory import ProcessorFactory
import threading
from abc import ABC, abstractmethod

class AbstractCrawler(ABC):

    def __init__(self, navigator, sources_metadata, error_handler,
        page_visit_handler, price_handler, stop_criteria, navigation_strategy, processor_type=ProcessorType.HtmlChunkProcessor.value, debug_mode=False, num_threads=4):
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
        else:
            self.sources_and_types_visited = None

        self.results = ResultIntegrator()
        
        self.num_threads = num_threads
        
        self.navigator_lock = threading.RLock()   
        self.url_visited_lock = threading.Lock()  
        self.visited_types_lock = threading.Lock()
        self.results_lock = threading.Lock()      
        self.error_lock = threading.Lock()        
        self.debug_lock = threading.Lock()

        #Se declaran las clases auxiliares que ocuparemos
        processor_factory = ProcessorFactory()
        processor_factory.initialize_processor(
            self.navigation_strategy,
            self.sources_rules,
            self.navigator,
            self.navigator_lock,
            self.results,
            self.results_lock
        )
        self.processor = processor_factory.get_processor(processor_type)

    @abstractmethod
    def crawl(self) -> ResultIntegrator:
        """
        Multi-threaded crawl using ThreadPoolExecutor.
        Each thread fetches and processes URLs independently.
        """
        pass
