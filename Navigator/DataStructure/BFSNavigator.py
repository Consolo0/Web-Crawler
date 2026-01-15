from Navigator.DataStructure.AbstractNavigator import AbstractNavigator
from collections import deque

class BFSNavigator(AbstractNavigator):
    def __init__(self):
        self.elements = deque([])
    
    def add(self, element):
        self.elements.append(element)
    
    def get_element(self):
        if not self.is_empty():
            return self.elements.popleft()
        return None
    
    def is_empty(self) -> bool:
        return len(self.elements) == 0
