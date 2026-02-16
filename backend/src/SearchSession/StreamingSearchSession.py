from src.SearchSession.AbstractSearchSession import AbstractSearchSession
from src.Db.Db import Db
from src.SearchSession.Status.SessionStatus import SessionStatus
from datetime import datetime
from src.URLProvider.Sources.SourceOrchestator import SourceOrchestator
from src.URLProvider.URL.URLGenerator import URLGenerator
from src.CrawlerProcess.Crawler.StreamingCrawler import StreamingCrawler

class StreamingSearchSession(AbstractSearchSession):
    """
    Streaming version of SearchSession that yields results as they come.
    """
    
    def __init__(self, query, error_handler, page_visit_handler, price_handler, stop_criteria, navigation_strategy):
        super().__init__(query, error_handler, page_visit_handler, price_handler, stop_criteria, navigation_strategy)

    def execute(self, db: Db):
        """
        Execute search session and yield results as they come in.
        """
        self.start_time = datetime.now()

        try:
            # Initialize sources
            source_orchestator = SourceOrchestator(db)
            sources_metadata = source_orchestator.get_sources()

            # Generate URLs
            url_generator = URLGenerator(sources_metadata, self.query, self.associated_navigation_strategy)
            navigator = url_generator.run()

            # Create streaming crawler
            crawler = StreamingCrawler(
                navigator, 
                sources_metadata, 
                self.error_handler, 
                self.page_visit_handler, 
                self.price_handler, 
                self.associated_stop_criteria, 
                self.associated_navigation_strategy
            )
            
            # Stream results
            for event in crawler.crawl():
                yield event
            
            self.status = SessionStatus.FINISHED

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status = SessionStatus.ABORTED
            self.error_handler.add_element(e)
            
            # Yield error event
            yield {
                "type": "error",
                "message": "Session aborted",
                "error": str(e)
            }

        self.end_time = datetime.now()