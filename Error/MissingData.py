class MissingData(Exception):
    def __init__(self, message="Data is missing or incomplete."):
        self.message = message
        super().__init__(self.message)