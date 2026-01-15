class NavigationStrategy:
    def __init__(self, strategy : dict):
        self.Type = strategy.get("Type", "BFS")
        self.MaximnunDepth = strategy.get("MaximnunDepth", 5)