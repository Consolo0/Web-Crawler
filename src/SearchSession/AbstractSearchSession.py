from abc import ABC, abstractmethod
from src.SearchSession.Status.SessionStatus import SessionStatus

class AbstractSearchSession(ABC):
    def __init__(self, error_handler, page_visit_handler, price_handler, stop_criteria, navigation_strategy):
        self.start_time = None
        self.end_time = None
        self.total_time = 0
        self.status = 'pending'
        #self.associated_query = query_id   ############ IMPORTANTE ESTO
        self.error_handler = error_handler
        self.page_visit_handler = page_visit_handler
        self.price_handler = price_handler
        self.associated_stop_criteria = stop_criteria
        self.associated_navigation_strategy = navigation_strategy

    @abstractmethod
    def execute(self, query: str) -> SessionStatus:
        pass