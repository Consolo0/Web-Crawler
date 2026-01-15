from abc import ABC, abstractmethod

class AbstractNavigator(ABC):
    @abstractmethod
    def add(self, element):
        pass
    def get_element(self):
        pass
    def is_empty(self) -> bool:
        pass