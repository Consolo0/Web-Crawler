from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
from src.CrawlerProcess.ResultIntegrator.DataExtractor.DataExtractor import DataExtractor
from src.Enums.InfoType import InfoType


class MercadoLibreProcessor(AbstractListingProcessor):
    """
    Processor for MercadoLibre listing pages and product pages.
    
    How it works:
    1. Product links are in <a> tags with class "poly-component__title"
    2. The href attribute contains the full product URL
    3. Extract all hrefs and return them
    """

    def __init__(self, navigation_strategy):
        super().__init__(navigation_strategy)
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from MercadoLibre listing page using CSS selectors.
        """

        if not html_content or self.navigation_strategy.maximun_products_per_source - self.products_counter <= 0:
            return []
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        remaining_slots = self.navigation_strategy.maximun_products_per_source - self.products_counter
        product_links = soup.select(f"a.poly-component__title", limit=remaining_slots)
        self.products_counter += len(product_links)
        
        urls = []
        for link in product_links:
            href = link.get("href")
            if href:
                urls.append(href)
        
        return urls

    def extract_product_info(self, html: str) -> Dict:
        """
        Extract product information from MercadoLibre product pages.
        
        MercadoLibre uses JSON-LD structured data and JSON in script tags.
        Returns a dictionary with InfoType enum keys.
        """
        if not html:
            return {}
        
        soup = BeautifulSoup(html, "html.parser")
        product_info = {}
        
        # Try to extract from JSON-LD structured data first
        json_ld_data = DataExtractor.extract_json_ld(soup)
        
        # Extract Title
        title = None
        if json_ld_data and "name" in json_ld_data:
            title = json_ld_data.get("name")
        else:
            # Fallback to meta tags
            title_tag = soup.select_one("h1, .ui-pdp-title")
            if title_tag:
                title = title_tag.get_text(strip=True)
        product_info[InfoType.ProductTitle.value] = title
        
        # Extract Price
        price = None
        if json_ld_data and "offers" in json_ld_data:
            # Extract from JSON-LD offers
            offers = json_ld_data.get("offers", [])
            # Handle both single object and array formats
            if isinstance(offers, dict):
                offers = [offers]
            if offers and len(offers) > 0:
                price = offers[0].get("price")
                if price:
                    try:
                        price = float(price)
                    except (ValueError, TypeError):
                        price = None
        
        if not price:
            # Fallback to CSS selector
            price_tag = soup.select_one(".ui-pdp-price__second-line, [data-test='price']")
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                price = DataExtractor.extract_price_value(price_text)
        
        product_info[InfoType.Price.value] = price
        
        # Extract Stock (Availability)
        stock = None
        if json_ld_data and "offers" in json_ld_data:
            offers = json_ld_data.get("offers", [])
            # Handle both single object and array formats
            if isinstance(offers, dict):
                offers = [offers]
            if offers and len(offers) > 0:
                availability = offers[0].get("availability", "")
                stock = "InStock" in availability
        
        if stock is None:
            # Fallback to text search
            availability_tag = soup.select_one("[class*='availability'], .stock")
            if availability_tag:
                availability_text = availability_tag.get_text(strip=True).lower()
                stock = "agotado" not in availability_text and "sin stock" not in availability_text
        
        product_info[InfoType.Stock.value] = stock
        
        # Extract Rating
        rating = None
        rating_data = {
            "rating": None,
            "votes": None
        }
        
        if json_ld_data and "aggregateRating" in json_ld_data:
            rating_obj = json_ld_data.get("aggregateRating", {})
            rating = rating_obj.get("ratingValue")
            votes = rating_obj.get("ratingCount")
            if rating:
                try:
                    rating = float(rating)
                except (ValueError, TypeError):
                    rating = None
            if votes:
                try:
                    votes = int(votes)
                except (ValueError, TypeError):
                    votes = None
            rating_data["rating"] = rating
            rating_data["votes"] = votes
        else:
            # Fallback to selectors
            rating_tag = soup.select_one(".ui-pdp-review__rating, [data-test='rating']")
            if rating_tag:
                rating_text = rating_tag.get_text(strip=True)
                rating = DataExtractor.extract_rating_value(rating_text)
                rating_data["rating"] = rating
            
            votes_tag = soup.select_one(".ui-pdp-review__amount, [data-test='reviews']")
            if votes_tag:
                votes_text = votes_tag.get_text(strip=True)
                votes = DataExtractor.extract_votes_value(votes_text)
                rating_data["votes"] = votes
        
        product_info[InfoType.Rating.value] = rating_data if (rating_data["rating"] is not None or rating_data["votes"] is not None) else None
        
        return product_info
