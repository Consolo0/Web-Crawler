from Error.UnIdentifiedNavigator import UnIdentifiedNavigator
from Enums.NavigationStrategyType import NavigationStrategyType
class NavigatorOrchestrator:

    @staticmethod
    def get_navigator(navigation_strategy_type: str):
        if navigation_strategy_type == NavigationStrategyType.BFS:
            from DataStructure.BFSNavigator import BFSNavigator
            return BFSNavigator()
        
        elif navigation_strategy_type == NavigationStrategyType.DFS:
            from DataStructure.DFSNavigator import DFSNavigator
            return DFSNavigator()
        else:
            raise UnIdentifiedNavigator(type=navigation_strategy_type)