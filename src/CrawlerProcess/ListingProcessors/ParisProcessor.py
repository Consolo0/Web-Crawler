from typing import List
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor


class ParisProcessor(AbstractListingProcessor):
    """
    Processor for Paris.cl search listings.
    
    Product links are in <a class="pod pod-link"> tags with href attributes.
    """
    
    def extract_product_urls(self, html_content: str) -> List[str]:
        """
        Extract product URLs from Paris (Falabella) listing pages.
        
        Looks for <a class="pod-link"> tags which contain product URLs.
        """
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, "html.parser")
        urls = []
        
        # Find all product links - the main selector for Paris product cards
        product_links = soup.select("a.pod-link")
        
        for link in product_links:
            href = link.get("href")
            if href:
                # Clean up the URL (remove tracking parameters if needed, but keep the base URL)
                # URLs come with sponsoredClickData parameter but that's fine
                urls.append(href)
        
        return urls
