from AbstractController import AbstractController
from Db.Db import Db
from Error.NotSuccesfullySaved import NotSuccesfullySaved
from Handler.GeneralHandler import GeneralHandler
from Setters.SearchSesionRestrictions.NavigationStrategy import NavigationStrategy
from Setters.SearchSesionRestrictions.StopCriteria import StopCriteria

class Controller(AbstractController):
    def __init__(self, query: str, db: Db) -> None:
        super().__init__(query, db)

    def run(self, restrictions: dict) -> dict:
        is_query_saved = self.db.save(self.query)
        if not is_query_saved:
            raise NotSuccesfullySaved("Failed to save the query to the database.")
        
        error_handler = GeneralHandler()
        page_visit_handler = GeneralHandler()
        price_handler = GeneralHandler()

        stop_criteria = StopCriteria(restrictions.get("stop_criteria", {}))
        navigation_strategy = NavigationStrategy(restrictions.get("navigation_strategy", {}))

        SearchSession = SearchSession(error_handler, page_visit_handler, price_handler, stop_criteria, navigation_strategy)
        
        error_handler.save_in_db(self.db, 'Error')
        page_visit_handler.save_in_db(self.db, 'PageVisit')
        price_handler.save_in_db(self.db, 'Price')
        
        return SearchSession.execute(self.query)