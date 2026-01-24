from Navigator.DataStructure.AbstractNavigator import AbstractNavigator
from collections import deque

class BFSNavigator(AbstractNavigator):
    def __init__(self):
        self.urls = deque([])
    
    def add(self, source, url, level, page_type):
        self.urls.append((source, url, level, page_type))
    
    def get_element(self):
        if not self.is_empty():
            return self.urls.popleft()
        return None
    
    def is_empty(self) -> bool:
        return len(self.urls) == 0
