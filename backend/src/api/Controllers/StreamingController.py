from src.api.Controllers.AbstractController import AbstractController
from src.Db.Db import Db
from src.Handler.GeneralHandler import GeneralHandler
from src.Setters.SearchSesionRestrictions.NavigationStrategy import NavigationStrategy
from src.Setters.SearchSesionRestrictions.StopCriteria import StopCriteria
from src.SearchSession.StreamingSearchSession import StreamingSearchSession

class StreamingController(AbstractController):
    """
    Streaming version of Controller that yields results as they come.
    """
    
    def __init__(self, query: str, db: Db) -> None:
        super().__init__(query, db)

    def run(self, restrictions: dict):
        """
        Run the crawler and stream results as they come in.
        Yields events of different types: status, listing_result, error, done.
        """
        # Initialize handlers
        error_handler = GeneralHandler()
        page_visit_handler = GeneralHandler()
        price_handler = GeneralHandler()

        # Parse restrictions
        stop_criteria = StopCriteria(restrictions.get("stop_criteria", {}))
        navigation_strategy = NavigationStrategy(restrictions.get("navigation_strategy", {}))

        # Create streaming search session
        search_session = StreamingSearchSession(
            self.query, 
            error_handler, 
            page_visit_handler, 
            price_handler, 
            stop_criteria, 
            navigation_strategy
        )
        
        # Stream results
        for event in search_session.execute_stream(self.db):
            yield event
