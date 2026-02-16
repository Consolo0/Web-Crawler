from abc import ABC, abstractmethod
from src.Setters.Query.Query import Query
from src.Db.Db import Db

class AbstractController(ABC):
    def __init__(self, query : str, db: Db) -> None:
        self.query = Query(query)
        self.db = db

    @abstractmethod
    def run(self, restrictions: dict) -> dict:
        pass
