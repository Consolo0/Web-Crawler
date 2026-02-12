class UnrecognizedProcessorType(Exception):

    def __init__(self, expected_type, received_type, message="Not expected page processing type"):
        self.received_type = received_type
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: got {self.received_type}"