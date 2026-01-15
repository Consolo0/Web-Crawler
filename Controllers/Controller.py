from AbstractController import AbstractController
from Db.Db import Db
from Error.NotSuccesfullySaved import NotSuccesfullySaved
from Handler.GeneralHandler import GeneralHandler

class Controller(AbstractController):
    def __init__(self, query: str, db: Db) -> None:
        super().__init__(query, db)

    def run(self) -> dict:
        is_query_saved = self.db.save(self.query)
        if not is_query_saved:
            raise NotSuccesfullySaved("Failed to save the query to the database.")
        
        Error_handler = GeneralHandler()
        PageVisitHandler = GeneralHandler()
        PriceHandler = GeneralHandler()
        SearchSession = SearchSession(Error_handler, PageVisitHandler, PriceHandler)
        
        return SearchSession.execute(self.query)