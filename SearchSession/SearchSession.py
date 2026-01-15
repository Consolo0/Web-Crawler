from AbstractSearchSession import AbstractSearchSession
from Db.Db import Db
from SearchSession.Status import SessionStatus
from datetime import datetime
from URLProvider.Sources.SourceOrchestator import SourceOrchestator
from URLProvider.URL.URLGenerator import URLGenerator

class SearchSession(AbstractSearchSession):
    def __init__(self, error_handler, page_visit_handler, price_handler, stop_criteria, navigation_strategy):
        super().__init__(error_handler, page_visit_handler, price_handler, stop_criteria, navigation_strategy)

    def execute(self, query: str, db: Db) -> dict:
        self.start_time = datetime.now()

        try:
            source_orchestator = SourceOrchestator(db)
            sources_metadata = source_orchestator.get_sources()

            url_generator = URLGenerator(sources_metadata, query, self.navigation_strategy)
            navigator = url_generator.run()

            crawler = Crawler(navigator, sources_metadata)
            results = crawler.crawl()
            self.status = SessionStatus.FINISHED

        except Exception as e:
            self.status = SessionStatus.ABORTED
            self.error_handler.handle(e)
            results = {}

        self.end_time = datetime.now()

        db.save(self.stop_criteria, 'StopCriteria')
        db.save(self.navigation_strategy, 'NavigationStrategy')

        return results
