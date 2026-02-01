from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
from src.Enums.InfoType import InfoType


class FalabellaProcessor(AbstractListingProcessor):
    """
    Processor for Falabella.com search listings and product pages.
    
    Product links are in <a class="pod-link"> tags with href attributes.
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from Falabella listing pages.
        
        Looks for <a class="pod-link"> tags which contain product URLs.
        """
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, "html.parser")
        urls = []
        
        # Find all product links - the main selector for Falabella product cards
        product_links = soup.select("a.pod-link")
        
        for link in product_links:
            href = link.get("href")
            if href:
                # Clean up the URL (remove tracking parameters if needed, but keep the base URL)
                # URLs come with sponsoredClickData parameter but that's fine
                urls.append(href)
        
        return urls

    def extract_product_info(self, html: str) -> Dict:
        """
        Extract product information from Falabella product pages.
        
        Returns a dictionary with InfoType enum keys.
        """
        if not html:
            return {}
        
        soup = BeautifulSoup(html, "html.parser")
        product_info = {}
        
        # Extract Title
        title = None
        title_tag = soup.select_one("h1")
        if title_tag:
            title = title_tag.get_text(strip=True)
        product_info[InfoType.ProductTitle.value] = title
        
        # Extract Price
        price = None
        # Look for price in common Falabella selectors
        price_tag = soup.select_one("[data-test='price'], .price, .product-price, [class*='price']")
        if price_tag:
            price_text = price_tag.get_text(strip=True)
            # Extract numeric value from price
            price = self._extract_price_value(price_text)
        product_info[InfoType.Price.value] = price
        
        # Extract Stock
        stock = None
        # Check for availability indicators
        stock_tag = soup.select_one("[data-test='availability'], .availability, [class*='stock']")
        if stock_tag:
            stock_text = stock_tag.get_text(strip=True).lower()
            stock = "agotado" not in stock_text and "sin stock" not in stock_text
        product_info[InfoType.Stock.value] = stock
        
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
        
        votes_tag = soup.select_one("[data-test='reviews'], .reviews, [class*='reviews']")
        if votes_tag:
            votes_text = votes_tag.get_text(strip=True)
            votes = self._extract_votes_value(votes_text)
            if votes is not None:
                rating_data["votes"] = votes
        
        if rating is not None:
            rating_data["rating"] = rating
        
        product_info[InfoType.Rating.value] = rating_data if (rating_data["rating"] is not None or rating_data["votes"] is not None) else None
        
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
