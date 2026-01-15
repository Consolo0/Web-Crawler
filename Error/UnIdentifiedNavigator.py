class UnIdentifiedNavigator(Exception):
    def __init__(self, type: str, message : str="The navigator could not be identified.",):
        self.message = message
        self.type = type
        super().__init__(self.message)
    def __str__(self):
        return f'{self.type} -> {self.message}'