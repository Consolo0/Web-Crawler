from abc import ABC, abstractmethod
from Error.NotSuccesfullySaved import NotSuccesfullySaved
from Db.Db import Db
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
            is_saved = db.save(element, collection_name)
            if not is_saved:
                raise NotSuccesfullySaved(f"Failed to save element: {element}")
        return True