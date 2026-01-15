from Error.UnIdentifiedNavigator import UnIdentifiedNavigator
class NavigatorOrchestrator:

    @staticmethod
    def get_navigator(navigation_strategy: str):
        if navigation_strategy == "BreadthFirst":
            from DataStructure.BFSNavigator import BFSNavigator
            return BFSNavigator()
        
        elif navigation_strategy == "DepthFirst":
            from DataStructure.DFSNavigator import DFSNavigator
            return DFSNavigator()
        else:
            raise UnIdentifiedNavigator(type=navigation_strategy)