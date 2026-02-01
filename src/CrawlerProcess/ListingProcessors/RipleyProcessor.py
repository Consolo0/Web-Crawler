from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
from src.Enums.InfoType import InfoType
import traceback


class RipleyProcessor(AbstractListingProcessor):
    """
    Processor for Ripley search listings and product pages.
    
    Ripley uses React with dynamic content loading.
    Looks for product containers and extracts URLs from links.
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from Ripley listing pages.
        
        Args:
            html_content: HTML content of the listing page
            
        Returns:
            List of product URLs
        """
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, "html.parser")
        urls = []
        
        # Ripley product URLs follow pattern: /p/productname-productid
        # Look for all links that match Ripley's product URL pattern
        selectors = [
            'a[href*="/p/"]',              # Product link pattern: /p/name-id
            'a.product-link',
            'a.item-link',
            'div.catalog-product-item a',
            'div[class*="product"] a[href*="ripley"]',
        ]
        
        for selector in selectors:
            try:
                links = soup.select(selector)
                for link in links:
                    href = link.get("href")
                    if href and "/p/" in href:
                        # Ensure absolute URL
                        if not href.startswith("http"):
                            if href.startswith("/"):
                                href = "https://simple.ripley.cl" + href
                            else:
                                href = "https://simple.ripley.cl/" + href
                        
                        # Avoid duplicates
                        if href not in urls and "ripley.cl" in href:
                            urls.append(href)
            except Exception as e:
                traceback.print_exc()
                continue
        
        return urls[:100]  # Limit to 100 products per page

    def extract_product_info(self, html: str) -> Dict:
        """
        Extract product information from Ripley product pages.
        
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
    Processor for Ripley search listings.
    
    Ripley uses React with dynamic content loading.
    Looks for product containers and extracts URLs from links.
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from Ripley listing pages.
        
        Args:
            html_content: HTML content of the listing page
            
        Returns:
            List of product URLs
        """
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, "html.parser")
        urls = []
        
        # Ripley product URLs follow pattern: /p/productname-productid
        # Look for all links that match Ripley's product URL pattern
        selectors = [
            'a[href*="/p/"]',              # Product link pattern: /p/name-id
            'a.product-link',
            'a.item-link',
            'div.catalog-product-item a',
            'div[class*="product"] a[href*="ripley"]',
        ]
        
        for selector in selectors:
            try:
                links = soup.select(selector)
                for link in links:
                    href = link.get("href")
                    if href and "/p/" in href:
                        # Ensure absolute URL
                        if not href.startswith("http"):
                            if href.startswith("/"):
                                href = "https://simple.ripley.cl" + href
                            else:
                                href = "https://simple.ripley.cl/" + href
                        
                        # Avoid duplicates
                        if href not in urls and "ripley.cl" in href:
                            urls.append(href)
            except Exception as e:
                traceback.print_exc()
                continue
        
        return urls[:100]  # Limit to 100 products per page
