class IndexOutOfRangeInHandler(Exception):

    def __init__(self, message="Index out of range in handler operation"):
        self.message = message
        super().__init__(self.message)