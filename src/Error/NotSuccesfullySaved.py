class NotSuccesfullySaved(Exception):
    def __init__(self, message="The data could not be saved successfully.") -> None:
        self.message = message
        super().__init__(self.message)
    