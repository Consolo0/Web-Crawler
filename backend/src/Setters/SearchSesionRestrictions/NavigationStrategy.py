from src.Enums.NavigationStrategyType import NavigationStrategyType

class NavigationStrategy:

    def __init__(self, strategy_params: dict = None):
        if strategy_params is None:
            strategy_params = {}
        self._type = strategy_params.get("type", NavigationStrategyType.BFS.value)
        self._maximum_depth = strategy_params.get("maximum_depth", 5)
        self._maximun_products_per_source = strategy_params.get("maximum_products_per_source", 1)

    @property
    def type(self) -> str:
        return self._type
    @property
    def maximum_depth(self) -> int:
        return self._maximum_depth
    @property
    def maximun_products_per_source(self) -> int:
        return self._maximun_products_per_source
