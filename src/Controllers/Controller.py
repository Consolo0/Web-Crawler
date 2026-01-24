from src.Controllers.AbstractController import AbstractController
from src.Db.Db import Db
from src.Error.NotSuccesfullySaved import NotSuccesfullySaved
from src.Handler.GeneralHandler import GeneralHandler
from src.Setters.SearchSesionRestrictions.NavigationStrategy import NavigationStrategy
from src.Setters.SearchSesionRestrictions.StopCriteria import StopCriteria
from src.SearchSession.SearchSession import SearchSession

class Controller(AbstractController):
    def __init__(self, query: str, db: Db) -> None:
        super().__init__(query, db)

    def run(self, restrictions: dict) -> dict:
        """query_saved, _ = self.db.save(self.query)
        if not query_saved:
            raise NotSuccesfullySaved("Failed to save the query to the database.")
        """
        error_handler = GeneralHandler()
        page_visit_handler = GeneralHandler()
        price_handler = GeneralHandler()

        print('Todos los handler creados')

        stop_criteria = StopCriteria(restrictions.get("stop_criteria", {}))
        navigation_strategy = NavigationStrategy(restrictions.get("navigation_strategy", {}))
        print("Stop y Navigation creados")
        
        search_session = SearchSession(error_handler, page_visit_handler, price_handler, stop_criteria, navigation_strategy)
        print("Search Session creado")
        result = search_session.execute(self.query)
        
        """error_handler.save_in_db(self.db, 'Error')
        page_visit_handler.save_in_db(self.db, 'PageVisit')
        price_handler.save_in_db(self.db, 'Price')

        Principal error es que cada error y pagevisit necesita el searchsession id
        y el price necesita el pagevisit
        """
        
        return result