class NavigationStrategy:

    def __init__(self, strategy_params: dict = None):
        if strategy_params is None:
            strategy_params = {}
        self._type = strategy_params.get("type", "BreadthFirst")
        self._maximum_depth = strategy_params.get("maximum_depth", 5)

        @property
        def type(self) -> str:
            return self._type
        @property
        def maximum_depth(self) -> int:
            return self._maximum_depth
