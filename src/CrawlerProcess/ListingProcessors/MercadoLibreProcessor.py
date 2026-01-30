from typing import List
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor


class MercadoLibreProcessor(AbstractListingProcessor):
    """
    Processor for MercadoLibre listing pages.
    
    How it works:
    1. Product links are in <a> tags with class "poly-component__title"
    2. The href attribute contains the full product URL
    3. Extract all hrefs and return them
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from MercadoLibre listing page using CSS selectors.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find all product links: <a class="poly-component__title" href="...">
        product_links = soup.select("a.poly-component__title")
        
        urls = []
        for link in product_links:
            href = link.get("href")
            if href:
                # Clean up the URL (remove tracking parameters if needed)
                # The URL comes with #polycard_client=... but that's fine
                urls.append(href)
        
        return urls
