from collections import defaultdict

class ResultIntegrator:

    def __init__(self):
        self.results = defaultdict(dict)

    def add_result(self, source_id, url, data):
        if data:
            self.results[source_id][url] = data

    def retrieve_dict(self):
        return [self.results[key] for key in self.results.keys()]

    def stringify_result(self):
        return str(self.retrieve_dict())
    
    def __str__(self):
        return self.stringify_result()