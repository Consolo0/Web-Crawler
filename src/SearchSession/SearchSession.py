from .AbstractSearchSession import AbstractSearchSession
from src.Db.Db import Db
from src.SearchSession.Status.SessionStatus import SessionStatus
from datetime import datetime
from src.URLProvider.Sources.SourceOrchestator import SourceOrchestator
from src.URLProvider.URL.URLGenerator import URLGenerator
from src.CrawlerProcess.Crawler import Crawler
from src.CrawlerProcess.ResultIntegrator.ResultIntegrator import ResultIntegrator

class SearchSession(AbstractSearchSession):
    def __init__(self, query, error_handler, page_visit_handler, price_handler, stop_criteria, navigation_strategy):
        super().__init__(query, error_handler, page_visit_handler, price_handler, stop_criteria, navigation_strategy)

    def execute(self, query: str, db: Db) -> ResultIntegrator:
        self.start_time = datetime.now()

        try:
            source_orchestator = SourceOrchestator(db)
            sources_metadata = source_orchestator.get_sources()

            url_generator = URLGenerator(sources_metadata, self.query, self.associated_navigation_strategy)
            navigator = url_generator.run()
            
            crawler = Crawler(navigator, sources_metadata, self.error_handler, self.page_visit_handler, self.price_handler, self.associated_stop_criteria, debug_mode = True)
            results = crawler.crawl() #lo que entrega muy probablemente cambie
            self.status = SessionStatus.FINISHED

        except Exception as e:
            self.status = SessionStatus.ABORTED
            self.error_handler.add_element(e)
            results = {}

        self.end_time = datetime.now()

        """stop_criteria_collecion, stop_criteria_id = db.save(self.stop_criteria, 'StopCriteria')
        nav_strategy_collecion, nav_strategy_id = db.save(self.navigation_strategy, 'NavigationStrategy')
        """
        return results
