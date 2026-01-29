from abc import ABC, abstractmethod

class AbstractNavigator(ABC):
    @abstractmethod
    def add(self, source, url, level, page_type):
        pass
    @abstractmethod
    def get_element(self):
        pass
    @abstractmethod
    def is_empty(self) -> bool:
        pass