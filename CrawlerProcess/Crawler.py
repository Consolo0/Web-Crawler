from collections import defaultdict
import re
from CutEvaluator.CutEvaluator import CutEvaluator

class Crawler:

    def __init__(self, navigator, sources_metadata, error_handler,
                 page_visit_handler, price_handler, stop_criteria):
        self.navigator = navigator
        self.sources_rules = sources_metadata
        self.error_handler = error_handler
        self.page_visit_handler = page_visit_handler
        self.price_handler = price_handler
        self.cut_evaluator = CutEvaluator(stop_criteria)
        self.url_visited = set()
        self.fetcher = Fetcher()

        self.errors_per_sources = defaultdict(int)
        self.results = defaultdict(dict)

    def crawl(self):

        while not self.navigator.is_empty():
            source_id, url, level, page_type = self.navigator.get_element()

            if url in self.url_visited:
                continue

            source_ctx = self.sources_rules.get(source_id)

            if not source_ctx:
                continue

            try:
                if not self._is_url_allowed(url, source_ctx["ValidationRules"]):
                    continue

                # ─────────────────────────────────────────────
                # 2. FETCH PAGE (API NOT PROVIDED)
                # ─────────────────────────────────────────────
                # This MUST be provided by navigator or another component

                """
                FALTANTE HACER EL FETCHER
                """
                html = self.fetcher.fetch(url)
                if not html:
                    continue
                self.url_visited.add(url)

                if page_type in ("search", "category"):
                    self._process_listing_page(
                        source_id,
                        html,
                        source_ctx["NavRules"],
                        level
                    )

                elif page_type == "product":
                    data = self._process_product_page(
                        html,
                        source_ctx["ExtractionRules"]
                    )
                    if data:
                        self.results[source_id][url] = data
                

                # ─────────────────────────────────────────────
                # 4. CUT EVALUATOR
                # ─────────────────────────────────────────────
                if not self.cut_evaluator.should_continue(
                    errors=self.errors_per_sources[source_id]
                ):
                    break

            except Exception as e:
                self.errors_per_sources[source_id] += 1
                self.error_handler.add_element((source_id, url, e))

    def _is_url_allowed(self, url, validation_rules):
        for rule in validation_rules:
            for pattern in rule.get("AllowedPaths", []):
                if re.search(pattern, url):
                    return True
        return False
    
    def _process_listing_page(self, source_id, html, nav_rules, level):
        for rule in nav_rules:
            selectors = rule.get("Selectors")
            if not selectors:
                continue

            links = html.select(selectors)
            for link in links:
                href = link.get("href")
                if not href:
                    continue

                self.navigator.add_element(
                    source_id=source_id,
                    url=href,
                    level=level + 1,
                    page_type="product"
                )
    
    def _process_product_page(self, html, extraction_rules):
        extracted = {}

        # group by entity type
        rules_by_entity = defaultdict(list)
        for rule in extraction_rules:
            rules_by_entity[rule["AssociatedSourceRule"]].append(rule)

        for entity, rules in rules_by_entity.items():
            rules.sort(key=lambda r: r.get("Priority", 1))

            for rule in rules:
                selector = rule["Selector"]
                attr = rule["Attribute"]

                nodes = html.select(selector)
                if not nodes:
                    continue

                if attr == "text":
                    value = nodes[0].get_text(strip=True)
                elif attr == "existence":
                    value = True
                else:
                    value = nodes[0].get(attr)

                if value:
                    extracted[entity] = value
                    break  # fallback handled

        if "Price" in extracted:
            extracted["Price"] = TextNormalizer.normalize(
                extracted["Price"]
            )

        return extracted


