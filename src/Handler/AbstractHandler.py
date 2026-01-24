from abc import ABC, abstractmethod
from src.Error.NotSuccesfullySaved import NotSuccesfullySaved
from src.Db.Db import Db
class AbstractHandler(ABC):
    def __init__(self):
        self.__elements = []

    @property
    def elements(self):
        return self.__elements
    @abstractmethod
    def add_element(self, element):
        pass
    @abstractmethod
    def clear_elements(self):
        pass
    @abstractmethod
    def pop(self, index):
        pass
    def save_in_db(self, db: Db, collection_name: str) -> bool:
        for element in self.elements:
            collection_saved, _ = db.save(element, collection_name)
            if not collection_saved:
                raise NotSuccesfullySaved(f"Failed to save element: {element}")
        return True