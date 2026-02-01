from typing import List, Dict, Optional
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
import traceback
import re
import json
from bs4 import BeautifulSoup
from src.Enums.InfoType import InfoType

class LiderProcessor(AbstractListingProcessor):
    """
    Processor for LIDER (Walmart Chile) product listings and product pages.
    
    LIDER has strong anti-bot protection (Walmart's protection).
    This processor attempts to:
    1. Extract JSON data if available
    2. Fall back to CSS selectors for product links
    
    IMPORTANT: LIDER actively blocks bots. If you see "Robot or human?" pages,
    the site is detecting automated access.
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from LIDER listing pages.
        
        Args:
            html_content: HTML content of the listing page
            
        Returns:
            List of product URLs
        """
        
        # Try multiple approaches in order of preference
        urls = []
        
        # Approach 1: Look for JSON data in window.__INITIAL_STATE__ (common pattern)
        urls = self._extract_from_initial_state(html_content)
        if urls:
            return urls
        
        # Approach 2: Look for other JSON patterns
        urls = self._extract_from_json_script(html_content)
        if urls:
            return urls
        
        # Approach 3: Fall back to CSS selectors
        urls = self._extract_from_css_selectors(html_content)
        if urls:
            return urls
        
        return []
    
    def extract_product_info(self, html: str) -> Dict:
        """
        Extract product information from LIDER product pages.
        
        Returns a dictionary with InfoType enum keys.
        """
        if not html:
            return {}
        
        soup = BeautifulSoup(html, "html.parser")
        product_info = {}
        
        # Extract Title
        title = None
        title_tag = soup.select_one("h1, .product-title, [data-test='product-title']")
        if title_tag:
            title = title_tag.get_text(strip=True)
        product_info[InfoType.ProductTitle] = title
        
        # Extract Price
        price = None
        price_tag = soup.select_one(".product-price, [data-test='price'], .price, [class*='price']")
        if price_tag:
            price_text = price_tag.get_text(strip=True)
            price = self._extract_price_value(price_text)
        product_info[InfoType.Price] = price
        
        # Extract Stock
        stock = None
        stock_tag = soup.select_one("[data-test='availability'], .availability, [class*='stock']")
        if stock_tag:
            stock_text = stock_tag.get_text(strip=True).lower()
            stock = "agotado" not in stock_text and "sin stock" not in stock_text
        product_info[InfoType.Stock] = stock
        
        # Extract Rating
        rating = None
        rating_data = {
            "rating": None,
            "votes": None
        }
        rating_tag = soup.select_one("[data-test='rating'], .rating, [class*='rating']")
        if rating_tag:
            rating_text = rating_tag.get_text(strip=True)
            rating = self._extract_rating_value(rating_text)
            rating_data["rating"] = rating
        
        votes_tag = soup.select_one("[data-test='reviews'], .reviews, [class*='reviews']")
        if votes_tag:
            votes_text = votes_tag.get_text(strip=True)
            votes = self._extract_votes_value(votes_text)
            rating_data["votes"] = votes
        
        product_info[InfoType.Rating] = rating_data if (rating_data["rating"] is not None or rating_data["votes"] is not None) else None
        
        return product_info
    
    def _extract_from_initial_state(self, html_content: str) -> List[str]:
        """Extract URLs from window.__INITIAL_STATE__ pattern"""
        
        # Look for window.__INITIAL_STATE__ = {...}
        pattern = r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            return []
        
        try:
            data = json.loads(match.group(1))
            
            # Navigate through common LIDER structure
            # Adjust these paths based on actual LIDER data structure
            products = data.get("products", {}).get("items", [])
            
            urls = []
            for product in products:
                if isinstance(product, dict):
                    # LIDER uses 'url' or 'href' for product links
                    url = product.get("url") or product.get("href") or product.get("link")
                    if url:
                        urls.append(url)
            
            return urls
        except Exception as e:
            traceback.print_exc()
            return []
    
    def _extract_from_json_script(self, html_content: str) -> List[str]:
        """Extract URLs from other JSON patterns"""
        
        # Look for various JSON patterns in script tags
        patterns = [
            r'var\s+products\s*=\s*(\[.*?\]);',
            r'var\s+items\s*=\s*(\[.*?\]);',
            r'"products"\s*:\s*(\[.*?\])',
            r'"items"\s*:\s*(\[.*?\])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    urls = []
                    for product in data:
                        if isinstance(product, dict):
                            url = product.get("url") or product.get("href") or product.get("link")
                            if url:
                                urls.append(url)
                    if urls:
                        return urls
                except:
                    continue
        
        return []
    
    def _extract_from_css_selectors(self, html_content: str) -> List[str]:
        """Fall back to CSS selectors"""
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Try multiple CSS selectors that commonly appear on LIDER
        selectors = [
            "a[href*='/producto/']",  # LIDER product pattern
            "a[href*='productid=']",
            "a.product-link",
            "a.item-link",
            "div.product a",
            "li.product a",
        ]
        
        for selector in selectors:
            try:
                links = soup.select(selector)
                urls = []
                for link in links:
                    href = link.get("href")
                    if href:
                        # Convert relative URLs to absolute if needed
                        if href.startswith("/"):
                            href = "https://lider.cl" + href
                        elif not href.startswith("http"):
                            href = "https://lider.cl/" + href
                        urls.append(href)
                
                if urls:
                    return urls
            except:
                continue
        
        return []

    @staticmethod
    def _extract_price_value(text: str) -> Optional[float]:
        """Extract numeric price from text."""
        if not text:
            return None
        try:
            # Remove common currency symbols and spaces
            clean = re.sub(r'[^\d.,]', '', text).strip()
            if clean:
                # Replace comma with dot for decimal
                clean = clean.replace(',', '.')
                return float(clean)
        except (ValueError, AttributeError):
            pass
        return None

    @staticmethod
    def _extract_rating_value(text: str) -> Optional[float]:
        """Extract rating value from text."""
        if not text:
            return None
        try:
            # Extract first number that looks like a rating (0-5)
            match = re.search(r'(\d+\.?\d*)', text)
            if match:
                rating = float(match.group(1))
                if 0 <= rating <= 5:
                    return rating
        except (ValueError, AttributeError):
            pass
        return None

    @staticmethod
    def _extract_votes_value(text: str) -> Optional[int]:
        """Extract number of votes from text."""
        if not text:
            return None
        try:
            # Extract the number
            match = re.search(r'(\d+)', text)
            if match:
                return int(match.group(1))
        except (ValueError, AttributeError):
            pass
        return None

    """
    Processor for LIDER (Walmart Chile) product listings.
    
    LIDER has strong anti-bot protection (Walmart's protection).
    This processor attempts to:
    1. Extract JSON data if available
    2. Fall back to CSS selectors for product links
    
    IMPORTANT: LIDER actively blocks bots. If you see "Robot or human?" pages,
    the site is detecting automated access.
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from LIDER listing pages.
        
        Args:
            html_content: HTML content of the listing page
            
        Returns:
            List of product URLs
        """
        
        # Try multiple approaches in order of preference
        urls = []
        
        # Approach 1: Look for JSON data in window.__INITIAL_STATE__ (common pattern)
        urls = self._extract_from_initial_state(html_content)
        if urls:
            return urls
        
        # Approach 2: Look for other JSON patterns
        urls = self._extract_from_json_script(html_content)
        if urls:
            return urls
        
        # Approach 3: Fall back to CSS selectors
        urls = self._extract_from_css_selectors(html_content)
        if urls:
            return urls
        
        return []
    
    def _extract_from_initial_state(self, html_content: str) -> List[str]:
        """Extract URLs from window.__INITIAL_STATE__ pattern"""
        import re
        import json
        
        # Look for window.__INITIAL_STATE__ = {...}
        pattern = r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            return []
        
        try:
            data = json.loads(match.group(1))
            
            # Navigate through common LIDER structure
            # Adjust these paths based on actual LIDER data structure
            products = data.get("products", {}).get("items", [])
            
            urls = []
            for product in products:
                if isinstance(product, dict):
                    # LIDER uses 'url' or 'href' for product links
                    url = product.get("url") or product.get("href") or product.get("link")
                    if url:
                        urls.append(url)
            
            return urls
        except Exception as e:
            traceback.print_exc()
            return []
    
    def _extract_from_json_script(self, html_content: str) -> List[str]:
        """Extract URLs from other JSON patterns"""
        import re
        import json
        
        # Look for various JSON patterns in script tags
        patterns = [
            r'var\s+products\s*=\s*(\[.*?\]);',
            r'var\s+items\s*=\s*(\[.*?\]);',
            r'"products"\s*:\s*(\[.*?\])',
            r'"items"\s*:\s*(\[.*?\])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    urls = []
                    for product in data:
                        if isinstance(product, dict):
                            url = product.get("url") or product.get("href") or product.get("link")
                            if url:
                                urls.append(url)
                    if urls:
                        return urls
                except:
                    continue
        
        return []
    
    def _extract_from_css_selectors(self, html_content: str) -> List[str]:
        """Fall back to CSS selectors"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Try multiple CSS selectors that commonly appear on LIDER
        selectors = [
            "a[href*='/producto/']",  # LIDER product pattern
            "a[href*='productid=']",
            "a.product-link",
            "a.item-link",
            "div.product a",
            "li.product a",
        ]
        
        for selector in selectors:
            try:
                links = soup.select(selector)
                urls = []
                for link in links:
                    href = link.get("href")
                    if href:
                        # Convert relative URLs to absolute if needed
                        if href.startswith("/"):
                            href = "https://lider.cl" + href
                        elif not href.startswith("http"):
                            href = "https://lider.cl/" + href
                        urls.append(href)
                
                if urls:
                    return urls
            except:
                continue
        
        return []
