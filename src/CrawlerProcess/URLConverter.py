from typing import List


class URLConverter:
    """
    Converts relative URLs to absolute URLs.
    
    Follows Open/Closed Principle:
    - Open for extension: Can subclass for different conversion strategies
    - Closed for modification: Core logic doesn't change when adding new strategies
    
    Example:
        converter = URLConverter("paris.cl")
        converter.to_absolute(["/product.html", "https://example.com/other"])
        # Returns: ["https://paris.cl/product.html", "https://example.com/other"]
    """
    
    def __init__(self, domain: str):
        """
        Args:
            domain: Base domain without protocol (e.g., "paris.cl", "www.falabella.com")
        """
        self.domain = domain
    
    def to_absolute(self, urls: List[str]) -> List[str]:
        """
        Convert a list of URLs (relative or absolute) to absolute URLs.
        
        Args:
            urls: List of URLs (can be relative or absolute)
            
        Returns:
            List of absolute URLs
        """
        return [self._convert_single(url) for url in urls if url]
    
    def _convert_single(self, url: str) -> str:
        """
        Convert a single URL to absolute.
        
        Handles three cases:
        1. Already absolute: https://example.com/path → https://example.com/path
        2. Relative with slash: /path/to/page.html → https://domain/path/to/page.html
        3. Relative without slash: path/to/page.html → https://domain/path/to/page.html
        
        Args:
            url: Single URL to convert
            
        Returns:
            Absolute URL
        """
        if url.startswith("http://") or url.startswith("https://"):
            # Already absolute
            return url
        elif url.startswith("/"):
            # Relative path with leading slash
            return f"https://{self.domain}{url}"
        else:
            # Relative path without leading slash
            return f"https://{self.domain}/{url}"
