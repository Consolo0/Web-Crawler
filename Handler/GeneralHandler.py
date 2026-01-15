from Handler.AbstractHandler import AbstractHandler
from Error.IndexOutOfRangeInHandler import IndexOutOfRangeInHandler
class GeneralHandler(AbstractHandler):
    def __init__(self):
        super().__init__()
    
    def add_element(self, element):
        self.elements.append(element)
    def clear_elements(self):
        self.elements.clear()
    def pop(self, index):
        if 0 <= index < len(self.elements):
            return self.elements.pop(index)
        raise IndexOutOfRangeInHandler(f'Index out of range while trying to pop element.\nIndex: {index}, Size: {len(self.elements)}')