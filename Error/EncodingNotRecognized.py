class EncodingNotRecognizedError(Exception):
    def __init__(self, encoding, message="The encoding of the resource could not be recognized."):
        self.encoding = encoding
        self.message = message
        super().__init__(self.message)
    def __str__(self):
        return f'{self.message} Encoding provided: {self.encoding}'