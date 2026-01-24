class NotExpectedType(Exception):

    def __init__(self, expected_type, received_type, message="Received type does not match expected type"):
        self.expected_type = expected_type
        self.received_type = received_type
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: expected {self.expected_type}, but got {self.received_type}"