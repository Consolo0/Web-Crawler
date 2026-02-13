from typing import Dict
from bs4 import BeautifulSoup
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor
from typing import List
from src.CrawlerProcess.InfoExtractor.InfoExtractor import InfoExtractor
from src.Enums.InfoType import InfoType
from src.Error.NotExpectedType import NotExpectedType
import webbrowser
from pathlib import Path
import traceback

class HtmlChunkProcessor(AbstractListingProcessor):
    """
    Processor for search listings and extract the products html chunks for a more efficient search.

    No need to visit individual product pages.
    """
    def __init__(self, navigation_strategy, sources_rules, results, results_lock) -> None:
        super().__init__(navigation_strategy, sources_rules, results, results_lock)
        self.source_id = None

    def _process_product_page_safe_and_save(self, source_id, html, url):
        """Thread-safe wrapper for product page processing"""
        pass
    
    def _process_product_page(self, source_id, html):
        """
        Process a product page to extract product information.
        Expects html as a string, converts to BeautifulSoup for parsing.
        """
        pass
    
    def _process_listing_page_safe_and_save(self, source_id, html, level):
        data = self._process_listing_page(source_id, html)

        if data:
            with self.results_lock:
                self.results.add_result(source_id, level, data)

    def _process_listing_page(self, source_id, html):
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
            return []
    
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
                    if href.startswith("//"):
                        href = "https:" + href
                    elif href.startswith("/"):
                        href = page_metadata["base_url"] + href
                    elif not href.startswith("http"):
                        href = page_metadata["base_url"] + "/" + href
                    page_metadata["stylesheets"].append(href)

            for style_tag in soup.find_all("style"):
                if style_tag.string:
                    page_metadata["inline_styles"].append(style_tag.string)
            
            remaining_slots = self.navigation_strategy.maximun_products_per_source - self.products_counter_per_source[self.source_id]
            if remaining_slots == 0:
                return None
            
            product_cards = soup.select(selector, limit=remaining_slots)
            
            products = {}
            for i, card in enumerate(product_cards):
                html_string = str(card)
                products[f"product_{i}"] = html_string
            
            self.products_counter_per_source[self.source_id] += len(products)

            results = {
                "metadata": page_metadata,
                "products": products
            }
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
        print("✅ Preview abierto en el navegador")

    def save_html_preview(self, chunk_data: dict, output_path: str = "preview.html"):
        """
        Guarda el HTML extraído en un archivo para visualizar en el browser.
        """
        metadata = chunk_data.get("metadata", {})
        products = chunk_data.get("products", {})
        
        html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preview - Products</title>
        
        <!-- Cargar CSS externos -->
        {"".join([f'<link rel="stylesheet" href="{css}">' for css in metadata.get("stylesheets", [])])}
        
        <!-- Estilos inline -->
        {"".join([f'<style>{style}</style>' for style in metadata.get("inline_styles", [])])}
        
        <style>
            body {{
                margin: 20px;
                font-family: Arial, sans-serif;
            }}
            .product-container {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
                padding: 20px;
            }}
            .product-wrapper {{
                border: 2px solid #ddd;
                padding: 10px;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <h1>{f'Source: {self.source_id}'}</h1>
        <div class="product-container">
            {"".join([f'<div class="product-wrapper">{html}</div>' for html in products.values()])}
        </div>
    </body>
    </html>
    """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Preview guardado en: {output_path}")
        print(f"   Abre el archivo en tu navegador para ver el resultado")
