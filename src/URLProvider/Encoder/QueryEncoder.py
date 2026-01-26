from src.Error.EncodingNotRecognized import EncodingNotRecognizedError
class QueryEncoder:
    def __init__(self):
        self.encodings = {
            "slug": self.slug_encode,
            "url": self.url_encode,
            "urlencode": self.url_encode  # Map urlencode to url_encode
        }

    def encode(self, query: str, encoding_type: str) -> str:
        if encoding_type in self.encodings:
            return self.encodings[encoding_type](query)
        raise EncodingNotRecognizedError(encoding_type)
    def slug_encode(self, query: str) -> str:
        return query.lower().replace(" ", "-")
    def url_encode(self, query: str) -> str:
        from urllib.parse import quote_plus
        return quote_plus(query)