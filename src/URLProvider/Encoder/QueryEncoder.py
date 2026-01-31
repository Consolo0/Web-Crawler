from src.Error.EncodingNotRecognized import EncodingNotRecognizedError
class QueryEncoder:
    def __init__(self):
        self.encodings = {
            "slug": self.slug_encode,
            "url": self.url_encode,
            "urlencode": self.url_encode,
            "percentencode": self.percent_encode,
        }

    def encode(self, query: str, encoding_type: str) -> str:
        if encoding_type in self.encodings:
            return self.encodings[encoding_type](query)
        raise EncodingNotRecognizedError(encoding_type)
    
    def slug_encode(self, query: str) -> str:
        return query.lower().replace(" ", "-")
    
    def url_encode(self, query: str) -> str:
        """URL encoding with + for spaces (form data)"""
        from urllib.parse import quote_plus
        return quote_plus(query)
    
    def percent_encode(self, query: str) -> str:
        """Percent encoding with %20 for spaces (path/URL)"""
        from urllib.parse import quote
        return quote(query, safe='')