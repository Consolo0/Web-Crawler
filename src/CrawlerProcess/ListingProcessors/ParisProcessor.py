from typing import List
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor


class ParisProcessor(AbstractListingProcessor):
    """
    Processor for Paris.cl search listings.
    
    Product links are in <a> tags with id starting with "product-" 
    inside divs with data-cnstrc-item-id attribute.
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from Paris listing pages.
        
        Looks for <a id="product-*"> tags which contain product URLs.
        """
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, "html.parser")
        urls = []
        
        # Find all product links by id pattern: id="product-..."
        product_links = soup.select("a[id^='product-']")
        
        for link in product_links:
            href = link.get("href")
            if href:
                urls.append(href)
        
        return urls
