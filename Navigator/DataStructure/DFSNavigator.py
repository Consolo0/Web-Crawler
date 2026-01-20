
from DataStructure.AbstractNavigator import AbstractNavigator

class DFSNavigator(AbstractNavigator):
    def __init__(self):
        self.urls = []
    def add(self, source, url, level, page_type):
        self.urls.append((source, url, level, page_type))
    def get_element(self):
        if self.urls:
            return self.urls.pop()
        return None
    def is_empty(self) -> bool:
        return len(self.urls) == 0
