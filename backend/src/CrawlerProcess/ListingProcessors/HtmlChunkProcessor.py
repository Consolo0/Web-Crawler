from typing import Dict
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
from typing import List
from src.CrawlerProcess.InfoExtractor.InfoExtractor import InfoExtractor
from src.Enums.InfoType import InfoType
from src.Error.NotExpectedType import NotExpectedType
from src.CrawlerProcess.URLConverter import URLConverter
import webbrowser
from pathlib import Path
import traceback

class HtmlChunkProcessor(AbstractListingProcessor):
    """
    Processor for search listings and extract the products html chunks for a more efficient search.

    No need to visit individual product pages.
    """
    def __init__(self, navigation_strategy, sources_rules, results, results_lock, debug_mode=False) -> None:
        super().__init__(navigation_strategy, sources_rules, results, results_lock)
        self.source_id = None
        self.debug_mode = debug_mode

    def _process_product_page_safe_and_save(self, source_id, html, url) -> Dict:
        """Thread-safe wrapper for product page processing"""
        pass
    
    def _process_product_page(self, source_id, html):
        """
        Process a product page to extract product information.
        Expects html as a string, converts to BeautifulSoup for parsing.
        """
        pass
    
    def _process_listing_page_safe_and_save(self, source_id, html, level, url) -> Dict:
        data = self._process_listing_page(source_id, html)

        if data:
            with self.results_lock:
                self.results.add_result(source_id=source_id, url=url, data=data)             
        return data

    def _process_listing_page(self, source_id, html) -> Dict:
        """
        Process a listing page to extract product links.
        
        This now uses the factory pattern to get the appropriate processor:
        - If the source has a custom processor (JSON extraction), use it
        - Otherwise, fall back to CSS selectors
        """
        try:
            return self.extract_product_info(source_id, html)
        
        except Exception as e:
            traceback.print_exc()
            return {"metadata": {}, "raw_html": html}
    
    def extract_product_info(self, source_id: str, html: str) -> Dict:
        """
        Extract raw HTML chunks of each product card from the listing page.
        Returns a list of HTML strings, one for each product.
        """
        if not html:
            return {}

        self.source_id = source_id
        soup = BeautifulSoup(html, "html.parser")
        html_chunks = {}
        extraction_rules = self.sources_rules[source_id].get("ExtractionRules")
        info_extractor = InfoExtractor(html_chunks, soup, None, extraction_rules)

        info_extractor.extract_info_and_save_it(InfoType.ProductChunk.value, self.extract_html_chunk)
        return html_chunks
    
    def extract_html_chunk(self, soup: BeautifulSoup, json_ld_data: Dict, priority: str, extraction_rules: Dict) -> Dict:
        """
        Extract the chunk based on the selector
        """
        product_chunk_rules = extraction_rules.get(InfoType.ProductChunk.value, {})
        rule = product_chunk_rules[priority]
        selector = rule.get("Selector")
        attribute = rule.get("Attribute")

        if attribute == "html chunk":
            page_metadata = {
                "stylesheets": [],
                "inline_styles": [],
                "base_url": self.sources_rules[self.source_id]["Source"]["Domain"]
            }

            for link in soup.find_all("link", rel="stylesheet"):
                href = link.get("href")
                
                if href:
                    url_converter = URLConverter(self.sources_rules[self.source_id]["Source"]["Domain"])
                    href = url_converter._convert_single(href)
                    page_metadata["stylesheets"].append(href)

            for style_tag in soup.find_all("style"):
                if style_tag.string:
                    page_metadata["inline_styles"].append(style_tag.string)

            # Atomically reserve slots to prevent race conditions
            with self.products_counter_per_source_lock:
                products_retrieved = self.products_counter_per_source[self.source_id]
                remaining_slots = self.navigation_strategy.maximun_products_per_source - products_retrieved

                if remaining_slots <= 0:
                    return None
                
                # Reserve all remaining slots upfront - we'll release unused ones later
                self.products_counter_per_source[self.source_id] = products_retrieved + remaining_slots
            
            # Extract products without holding the lock (extraction is slow)
            product_cards = soup.select(selector, limit=remaining_slots)
            
            products = {}

            if product_cards:
                for i, card in enumerate(product_cards):
                    card_soup = BeautifulSoup(str(card), "html.parser")
                    url_converter = URLConverter(self.sources_rules[self.source_id]["Source"]["Domain"])

                    # Fix all relative hrefs
                    for a_tag in card_soup.find_all("a", href=True):
                        a_tag["href"] = url_converter._convert_single(a_tag["href"])
                        a_tag["target"] = "_blank"
                        a_tag["rel"] = "noopener noreferrer"

                    # Fix all images
                    for img_tag in card_soup.find_all("img"):
                        img_tag["loading"] = "eager"
                        classes = [c for c in img_tag.get("class", []) if c not in ("ui-opacity-0", "ui-absolute")]
                        img_tag["class"] = classes
                        if not img_tag.get("src"):
                            img_tag["src"] = (
                                img_tag.get("data-src") or
                                img_tag.get("data-lazy-src") or
                                img_tag.get("data-original")
                            )

                    # Remove skeletons
                    for skeleton in card_soup.find_all("div", attrs={"data-testid": "paris-skeleton"}):
                        skeleton.decompose()
                    for skeleton in card_soup.find_all("div", class_=lambda c: c and "skeleton" in " ".join(c)):
                        skeleton.decompose()

                    first_img = card_soup.find("img")
                    first_a = card_soup.find("a", href=True)

                    products[f"product_{i}"] = {
                        "html": str(card_soup),
                        "image": first_img.get("src") if first_img else None,
                        "href": first_a.get("href") if first_a else None
                    }

                # Adjust counter based on actual products extracted
                actual_count = len(products)
                if actual_count < remaining_slots:
                    with self.products_counter_per_source_lock:
                        # Release unused reserved slots
                        self.products_counter_per_source[self.source_id] -= (remaining_slots - actual_count)

                results = {
                    "metadata": page_metadata,
                    "products": products
                }

            else:
                results = {
                    "metadata": page_metadata,
                    "raw_html": str(soup)
                }

            if self.debug_mode:
                self.preview_html_in_browser(results)
            return results
        
        raise NotExpectedType("html chunk", attribute)

    def extract_product_urls(self, source_id: str, html_content: str) -> List[str]:
        pass

    def preview_html_in_browser(self, chunk_data: dict):
        """
        Crea un archivo temporal y lo abre en el navegador.
        """
        # Crear archivo temporal
        temp_file = Path("temp_preview.html")
        self.save_html_preview(chunk_data, str(temp_file))
    
        # Abrir en el navegador
        webbrowser.open(f'file://{temp_file.absolute()}')

    def save_html_preview(self, chunk_data: dict, output_path: str = "preview.html"):
        metadata = chunk_data.get("metadata", {})
        products = chunk_data.get("products", {})

        products_html = "".join([html for html in products.values()])

        html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preview - Products</title>

        {"".join([f'<link rel="stylesheet" href="{css}">' for css in metadata.get("stylesheets", [])])}
        {"".join([f'<style>{style}</style>' for style in metadata.get("inline_styles", [])])}

        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}

            h1 {{
                margin-bottom: 20px;
            }}

            .product-container {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(240px, 250px));
                gap: 16px;
                width: 100%;
                max-width: 1400px;
                margin: 0 auto;
                justify-content: start;
            }}

            .product-container > * {{
                width: 242px !important;
                max-width: 242px !important;
                min-width: 242px !important;
                height: auto !important;
                max-height: none !important;
                overflow: visible !important;
            }}

            @media (max-width: 1200px) {{
                .product-container {{
                    grid-template-columns: repeat(auto-fill, minmax(240px, 250px));
                }}
            }}

            @media (max-width: 768px) {{
                .product-container {{
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                }}
                
                .product-container > * {{
                    width: 100% !important;
                    max-width: 100% !important;
                    min-width: 200px !important;
                }}
            }}
        </style>
    </head>
    <body>
        <h1>Source: {self.source_id} ({len(products)} productos)</h1>
        <div class="product-container">
            {products_html}
        </div>
    </body>
    </html>
    """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
