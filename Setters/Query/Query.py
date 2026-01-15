class Query():
    def __init__(self, query: str) -> None:
        self._query = query

    @property
    def query(self) -> str:
        return self._query
