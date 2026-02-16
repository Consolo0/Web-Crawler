import traceback
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from pathlib import Path
from src.CrawlerProcess.CutEvaluator.CutEvaluator import CutEvaluator
from src.CrawlerProcess.Fetch.Fetcher import Fetcher
from src.CrawlerProcess.ResultIntegrator.ResultIntegrator import ResultIntegrator
from src.CrawlerProcess.URLProcessor.StreamingURLProcessor import StreamingURLProcessor
from src.CrawlerProcess.ListingProcessors.ProcessorFactory import ProcessorFactory
from src.Enums.ProcessorType import ProcessorType
from src.CrawlerProcess.Crawler.AbstractCrawler import AbstractCrawler

class StreamingCrawler(AbstractCrawler):
    """
    Streaming version of Crawler that yields results as they come in.
    """

    def __init__(self, navigator, sources_metadata, error_handler,
        page_visit_handler, price_handler, stop_criteria, navigation_strategy, 
        processor_type=ProcessorType.HtmlChunkProcessor.value, debug_mode=False, num_threads=4):

        super().__init__(navigator, sources_metadata, error_handler,
        page_visit_handler, price_handler, stop_criteria, navigation_strategy, processor_type, debug_mode, num_threads)

        # Queue for streaming results from threads
        self.result_queue = Queue()

        self.URLProcessor = StreamingURLProcessor(
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

    def _process_url_and_queue(self, source_id, url, level, page_type):
        """
        Wrapper that processes URL and puts results in queue for main thread to yield.
        """
        try:
            # Process URL and get generator of results
            for result in self.URLProcessor._process_url(source_id, url, level, page_type):
                # Put result in queue for main thread to yield
                self.result_queue.put(("result", result))
        
        except Exception as e:
            # Put error in queue
            self.result_queue.put(("error", {
                "source_id": source_id,
                "url": url,
                "error": str(e)
            }))
            traceback.print_exc()

    def crawl(self):
        """
        Stream results as they come in from the crawler.
        Yields results incrementally instead of waiting for all to complete.
        """
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = set()
            total_submitted = 0
            total_completed = 0
            
            # Send initial status
            yield {
                "type": "status",
                "message": "Starting crawl",
                "submitted": 0,
                "completed": 0
            }
            
            while True:
                # Check stop criteria
                with self.error_lock:
                    if not self.cut_evaluator.should_continue(self.error_handler.get_length()):
                        yield {
                            "type": "status",
                            "message": "Stop criteria met",
                            "submitted": total_submitted,
                            "completed": total_completed
                        }
                        break

                # Try to submit new work
                got_item = False
                with self.navigator_lock:
                    if not self.navigator.is_empty() and len(futures) < self.num_threads:
                        source_id, url, level, page_type = self.navigator.get_element()
                        got_item = True

                if got_item:
                    # Check if already visited
                    with self.url_visited_lock:
                        if url in self.url_visited:
                            continue
                    
                    if self.debug_mode:
                        with self.visited_types_lock:
                            if (source_id, page_type) in self.sources_and_types_visited:
                                continue
                    
                    # Submit work
                    future = executor.submit(
                        self._process_url_and_queue,
                        source_id, url, level, page_type
                    )
                    futures.add(future)
                    total_submitted += 1
                    
                    yield {
                        "type": "status",
                        "message": f"Processing {source_id}...",
                        "submitted": total_submitted,
                        "completed": total_completed
                    }
                
                # Check for completed futures
                completed_futures = []
                for future in futures:
                    if future.done():
                        completed_futures.append(future)
                        total_completed += 1
                        
                        try:
                            future.result()  # Check for exceptions
                        except Exception as e:
                            traceback.print_exc()
                
                # Remove completed futures
                for future in completed_futures:
                    futures.discard(future)
                
                # Yield all available results from queue
                while not self.result_queue.empty():
                    msg_type, data = self.result_queue.get()
                    
                    if msg_type == "result":
                        yield data
                    
                    elif msg_type == "error":
                        yield {
                            "type": "error",
                            "data": data
                        }
                
                # Exit conditions
                if not got_item and not futures:
                    yield {
                        "type": "status",
                        "message": "Crawl complete - no more URLs",
                        "submitted": total_submitted,
                        "completed": total_completed
                    }
                    break
                
                # Small delay to prevent busy waiting if no new items but futures pending
                if not got_item and futures:
                    import time
                    time.sleep(0.1)
            
            # Wait for remaining futures
            for future in as_completed(futures):
                total_completed += 1
                try:
                    future.result()
                except Exception as e:
                    traceback.print_exc()
            
            # Yield any remaining results
            while not self.result_queue.empty():
                msg_type, data = self.result_queue.get()
                
                if msg_type == "result":
                    yield data
                
                elif msg_type == "error":
                    yield {
                            "type": "error",
                        "data": data
                    }
            
            # Send final results summary
            yield {
                "type": "done",
                "message": "All processing complete",
                "submitted": total_submitted,
                "completed": total_completed,
                "results": self.results
            }