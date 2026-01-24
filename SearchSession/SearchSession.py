from AbstractSearchSession import AbstractSearchSession
from Db.Db import Db
from SearchSession.Status import SessionStatus
from datetime import datetime
from URLProvider.Sources.SourceOrchestator import SourceOrchestator
from URLProvider.URL.URLGenerator import URLGenerator
from CrawlerProcess.Crawler import Crawler

class SearchSession(AbstractSearchSession):
    def __init__(self, error_handler, page_visit_handler, price_handler, stop_criteria, navigation_strategy):
        super().__init__(error_handler, page_visit_handler, price_handler, stop_criteria, navigation_strategy)

    def execute(self, query: str, db: Db) -> dict:
        self.start_time = datetime.now()

        try:
            source_orchestator = SourceOrchestator(db)
            sources_metadata = source_orchestator.get_sources()
            print("Creado la info de las sources")

            url_generator = URLGenerator(sources_metadata, query, self.navigation_strategy)
            navigator = url_generator.run()
            print("Creadas las urls y el navegador")
            
            crawler = Crawler(navigator, sources_metadata, self.error_handler, self.page_visit_handler, self.price_handler, self.associated_stop_criteria )
            results = crawler.crawl() #lo que entrega muy probablemente cambie
            self.status = SessionStatus.FINISHED

        except Exception as e:
            self.status = SessionStatus.ABORTED
            self.error_handler.handle(e)
            results = {}

        self.end_time = datetime.now()

        """stop_criteria_collecion, stop_criteria_id = db.save(self.stop_criteria, 'StopCriteria')
        nav_strategy_collecion, nav_strategy_id = db.save(self.navigation_strategy, 'NavigationStrategy')
        """
        return results
