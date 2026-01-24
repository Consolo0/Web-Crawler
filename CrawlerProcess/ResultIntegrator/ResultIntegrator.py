from collections import defaultdict

class ResultIntegrator:

    def __init__(self):
        self.results = defaultdict(dict)

    def add_result(self, source_id, url, data):
        if data:
            self.results[source_id][url] = data