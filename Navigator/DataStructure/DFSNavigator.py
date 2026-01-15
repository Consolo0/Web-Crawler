
from Navigator.DataStrucutre.AbstractNavigator import AbstractNavigator
class DFSNavigator(AbstractNavigator):
    def __init__(self):
        self.urls = []
    def add(self, url):
        self.urls.append(url)
    def get_element(self):
        if self.urls:
            return self.urls.pop()
        return None
    def is_empty(self) -> bool:
        return len(self.urls) == 0
