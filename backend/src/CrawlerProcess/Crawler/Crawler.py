import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.CrawlerProcess.ResultIntegrator.ResultIntegrator import ResultIntegrator
from src.Enums.ProcessorType import ProcessorType
from src.CrawlerProcess.Crawler import AbstractCrawler
from src.CrawlerProcess.URLProcessor.URLProcessor import URLProcessor

class Crawler(AbstractCrawler):

    def __init__(self, navigator, sources_metadata, error_handler,
        page_visit_handler, price_handler, stop_criteria, navigation_strategy, processor_type=ProcessorType.HtmlChunkProcessor.value, debug_mode=False, num_threads=4):
        
        super().__init__(navigator, sources_metadata, error_handler,
        page_visit_handler, price_handler, stop_criteria, navigation_strategy, processor_type, debug_mode, num_threads)

        self.URLProcessor = URLProcessor(
            sources_rules=self.sources_rules,
            fetcher=self.fetcher,
            url_visited=self.url_visited,
            url_visited_lock=self.url_visited_lock,
            error_handler=self.error_handler,
            error_lock=self.error_lock,
            sources_and_types_visited=self.sources_and_types_visited,
            processor=self.processor,
            debug_mode=self.debug_mode
        )
                

    def crawl(self) -> ResultIntegrator:
        """
        Multi-threaded crawl using ThreadPoolExecutor.
        Each thread fetches and processes URLs independently.
        """

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = set()
            
            while True:

                with self.error_lock:
                    if not self.cut_evaluator.should_continue(
                        self.error_handler.get_length()
                    ):
                        break

                got_item = False
                with self.navigator_lock:

                    if not self.navigator.is_empty() and len(futures) < self.num_threads:
                        source_id, url, level, page_type = self.navigator.get_element()
                        got_item = True

                if got_item:

                    with self.url_visited_lock:
                        if url in self.url_visited:
                            continue
                    
                    if self.debug_mode:
                        with self.visited_types_lock:
                            if (source_id, page_type) in self.sources_and_types_visited:
                                continue
                    
                    future = executor.submit(
                        self.URLProcessor._process_url,
                        source_id, url, level, page_type
                    )
                    futures.add(future)
                
                if not got_item and futures:
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
                    break
                
                if len(futures) >= self.num_threads * 2:
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
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    traceback.print_exc()
                finally:
                    futures.discard(future)
        
        return self.results
