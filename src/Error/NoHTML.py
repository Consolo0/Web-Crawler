class NoHTML(Exception):
    """Raised when no HTML content is fetched from a URL."""
    def __init__(self, message: str = "No HTML content fetched from the URL"):
        self.message = message
        super().__init__(self.message)