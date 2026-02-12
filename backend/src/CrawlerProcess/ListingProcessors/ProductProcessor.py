from typing import List, Dict
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
from src.CrawlerProcess.ResultIntegrator.DataExtractor.DataExtractor import DataExtractor
from src.CrawlerProcess.URLConverter import URLConverter
from src.Enums.InfoType import InfoType
import traceback

class ProductProcessor(AbstractListingProcessor):
    """
    Processor for search listings and product pages.
    
    Product links are in <a> tags with id starting with "product-" 
    inside divs with data-cnstrc-item-id attribute.
    """
    def __init__(self, navigation_strategy, sources_rules, navigator, navigator_lock, results, results_lock) -> None:
        super().__init__(navigation_strategy, sources_rules, results, results_lock)
        self.navigator = navigator
        self.navigator_lock = navigator_lock

    def _process_listing_page_safe_and_save(self, source_id, html, level):
        """Thread-safe wrapper for listing page processing and saving"""
        product_urls = self._process_listing_page(source_id, html)

        # Add product URLs to navigator (with lock)
        with self.navigator_lock:
            for product_url in product_urls:
                self.navigator.add(
                    source=source_id,
                    url=product_url,
                    level=level + 1,
                    page_type="product"
                )

    def _process_listing_page(self, source_id, html):
        """
        Process a listing page to extract product links.
        
        This now uses the factory pattern to get the appropriate processor:
        - If the source has a custom processor (JSON extraction), use it
        - Otherwise, fall back to CSS selectors
        """
        try:
            product_urls = self.extract_product_urls(source_id,html)
            
            source_domain = self.sources_rules[source_id]["Source"]["Domain"]
            converter = URLConverter(source_domain)
            absolute_urls = converter.to_absolute(product_urls)
            
            return absolute_urls
        
        except Exception as e:
            traceback.print_exc()
            return []
    
    def _process_product_page_safe_and_save(self, source_id, html, url):
        """Thread-safe wrapper for product page processing"""
        data = self._process_product_page(source_id, html)
        
        # Add results to ResultIntegrator (with lock)
        with self.results_lock:
            self.results.add_result(source_id, url, data)
    
    def _process_product_page(self, source_id, html):
        """
        Process a product page to extract product information.
        Expects html as a string, converts to BeautifulSoup for parsing.
        """
        extracted = {}  # Initialize to empty dict
        
        try:
            extracted = self.extract_product_info(source_id,html)

        except Exception as e:
            traceback.print_exc()
            # extracted remains empty dict if exception occurs

        return extracted
        
    def extract_product_urls(self, source_id: str, html_content: str) -> List[str]:
        """
        Extract product URLs from Page listing pages.
        
        Looks for <a id="product-*"> tags which contain product URLs.
        """
        if not html_content or self.navigation_strategy.maximun_products_per_source - self.products_counter_per_source[source_id] <= 0:
            return []
        
        soup = BeautifulSoup(html_content, "html.parser")
        urls = []
        nav_rules = self.sources_rules[source_id].get("NavRules")
        rules = nav_rules.get("search", {})
        selectors = rules.get("Selectors", "")
        attribute = rules.get("Link", "href")
        
        # Find all product links by id pattern: id="product-..."
        remaining_slots = self.navigation_strategy.maximun_products_per_source - self.products_counter_per_source[source_id]
        product_links = soup.select(f'{selectors}', limit=remaining_slots)
        self.products_counter_per_source[source_id] += len(product_links)
        
        for link in product_links:
            href = link.get(attribute)
            if href:
                urls.append(href)
        
        return urls

    def extract_product_info(self, source_id: str, html: str) -> Dict:
        """
        Extract product information from pages product pages.
        
        Pages uses JSON-LD structured data and Next.js data.
        Returns a dictionary with InfoType enum keys.
        """
        if not html:
            return {}
        
        soup = BeautifulSoup(html, "html.parser")
        product_info = {}
        
        # Try to extract from JSON-LD structured data first
        json_ld_data = DataExtractor.extract_json_ld(soup)
        
        #Ectraction rules
        extraction_rules = self.sources_rules[source_id].get("ExtractionRules")
        # Extract Title
        product_title_rules = extraction_rules.get("ProductTitle", {})

        for priority in sorted(product_title_rules.keys(), key=lambda x: int(x)):   

            if not InfoType.ProductTitle.value in product_info:
                title = self.extract_product_title(soup, json_ld_data, priority, extraction_rules)
                product_info[InfoType.ProductTitle.value] = title

                if title:
                    break
        
        # Extract Price
        product_price_rules = extraction_rules.get("Price", {})

        for priority in sorted(product_price_rules.keys(), key=lambda x: int(x)):

            if not InfoType.Price.value in product_info:
                price = self.extract_product_price(soup, json_ld_data, priority, extraction_rules)
                product_info[InfoType.Price.value] = price
                if price:
                    break
        
        # Extract Stock (Availability)
        product_stock_rules = extraction_rules.get("Stock", {})

        for priority in sorted(product_stock_rules.keys(), key=lambda x: int(x)):

            if not InfoType.Stock.value in product_info:
                stock = self.extract_product_stock(soup, json_ld_data, priority, extraction_rules)
                product_info[InfoType.Stock.value] = stock

                if stock:
                    break
        
        # Extract Rating
        product_rating_rules = extraction_rules.get("Rating", {})

        for priority in sorted(product_rating_rules.keys(), key=lambda x: int(x)):

            if not InfoType.Rating.value in product_info:
                rating_data = self.extract_product_rating(soup, json_ld_data, priority, extraction_rules)
                product_info[InfoType.Rating.value] = rating_data

                if rating_data:
                    break
        
        # Extract Votes
        for priority in sorted(product_rating_rules.keys(), key=lambda x: int(x)):

            if not InfoType.Votes.value in product_info:
                votes = self.extract_product_votes(soup, json_ld_data, priority, extraction_rules)
                product_info[InfoType.Votes.value] = votes

                if votes:
                    break
        
        return product_info
    
    def extract_product_title(self, soup: BeautifulSoup, json_ld_data: Dict, priority: str, extraction_rules: Dict) -> str:
            
            title = None
            product_title_rules = extraction_rules.get("ProductTitle", {})
            rule = product_title_rules[priority]
            selector = rule.get("Selector")
            attribute = rule.get("Attribute")

            if attribute == "json" and json_ld_data and selector in json_ld_data:
                title = json_ld_data.get(selector)

            elif attribute == "text":
                # Fallback to meta tags or h1
                title_tag = soup.select_one(selector)
                if title_tag:
                    title = title_tag.get_text(strip=True)

            return title

    def extract_product_price(self, soup: BeautifulSoup, json_ld_data: Dict, priority: str, extraction_rules: Dict):
        price = None
        product_price_rules = extraction_rules.get("Price", {})
        rule = product_price_rules[priority]
        selector = rule.get("Selector")
        attribute = rule.get("Attribute")

        if attribute == "json" and json_ld_data and selector in json_ld_data:
            # Extract from JSON-LD offers
            offers = json_ld_data.get(selector, [])
            # Handle both single object and array formats
            if isinstance(offers, dict):
                offers = [offers]

            if offers and len(offers) > 0:
                subselector = rule.get("SubSelector")
                price = offers[0].get(subselector)

                if price:
                    try:
                        price = float(price)
                    except (ValueError, TypeError):
                        price = None

        elif attribute == "text":

            price_tag = soup.select_one(selector)

            if price_tag:
                price_text = price_tag.get_text(strip=True)
                price = DataExtractor.extract_price_value(price_text)

        return price
    
    def extract_product_stock(self, soup: BeautifulSoup, json_ld_data: Dict, priority: str, extraction_rules: Dict):
        stock = None
        product_stock_rules = extraction_rules.get("Stock", {})
        rule = product_stock_rules[priority]
        selector = rule.get("Selector")
        attribute = rule.get("Attribute")

        if attribute == "json" and json_ld_data and selector in json_ld_data:
            
            offers = json_ld_data.get(selector, [])
            
            if isinstance(offers, dict):
                offers = [offers]
            if offers and len(offers) > 0:
                subselector = rule.get("SubSelector")
                availability = offers[0].get(subselector, "")
                stock = "InStock" in availability
        
        if stock is None:
            # Fallback to text search
            availability_tag = soup.select_one(selector)
            if availability_tag:
                availability_text = availability_tag.get_text(strip=True).lower()
                stock = "agotado" not in availability_text and "sin stock" not in availability_text

        return stock
    
    def extract_product_rating(self, soup: BeautifulSoup, json_ld_data: Dict, priority: str, extraction_rules: Dict):
        rating = None
        product_rating_rules = extraction_rules.get("Rating", {})
        rule = product_rating_rules[priority]
        selector = rule.get("Selector")
        attribute = rule.get("Attribute")

        if attribute == "json" and json_ld_data and selector in json_ld_data:
            rating_obj = json_ld_data.get(selector, {})
            subselector = rule.get("SubSelector")
            rating = rating_obj.get(subselector)

            if rating:
                try:
                    rating = float(rating)
                except (ValueError, TypeError):
                    rating = None

        elif attribute == "text":
            rating_tag = soup.select_one(selector)
            if rating_tag:
                rating_text = rating_tag.get_text(strip=True)
                rating = DataExtractor.extract_rating_value(rating_text)

        return rating
    
    def extract_product_votes(self, soup: BeautifulSoup, json_ld_data: Dict, priority: str, extraction_rules: Dict):
        votes = None
        product_votes_rules = extraction_rules.get("Votes", {})
        rule = product_votes_rules[priority]
        selector = rule.get("Selector")
        attribute = rule.get("Attribute")
    
        if attribute == "json" and json_ld_data and selector in json_ld_data:
            rating_obj = json_ld_data.get(selector, {})
            subselector = rule.get("SubSelector")
            votes = rating_obj.get(subselector)

            if votes:
                try:
                    votes = int(votes)
                except (ValueError, TypeError):
                    votes = None

        elif attribute == "text":
            
            votes_tag = soup.select_one(selector)
            if votes_tag:
                votes_text = votes_tag.get_text(strip=True)
                votes = DataExtractor.extract_votes_value(votes_text)
        
        return votes
