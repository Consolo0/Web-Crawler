from CutEvaluator.CutEvaluator import CutEvaluator

class Crawler:

    def __init__(self, navigator, sources_metadata, error_handler, page_visit_handler, price_handler, stop_criteria):
        self.navigator = navigator
        self.sources_rules = sources_metadata
        self.error_handler = error_handler
        self.page_visit_handler = page_visit_handler
        self.price_handler = price_handler
        self.cut_evaluator = CutEvaluator(stop_criteria)
        self.results = {}

    def crawl(self):
        
        while not self.navigator.is_empty():
            source, url, level, page_type = self.navigator.get_element()

            #1. hacemos la request url
            #llenar

            #2. dependiendo del page type, obtenemos su selector de soruces_rules con source
            #si es page_type igual a product, obtenemos los selectors de ExtractionRules

            #3.1 Si es una pagina tipo categoria o search, agregamos la url del producto en href
            #con level+1 y page_type product
            #3.2 Si es pagina tipo producto, tenemos los datos que queremos y los agregamos a results

            #4 Cut Evaluator chequea si seguimos

            #5 Si se corto el flujo, contactamos a result integrator