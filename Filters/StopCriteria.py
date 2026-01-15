class StopCriteria:
    def __init__(self, stop_criteria : dict):
        self.TimeOut = stop_criteria.get("TimeOut", 300)
        self.MaximunErrors = stop_criteria.get("MaximunErrors", 5)
        self.MinimumResults = stop_criteria.get("MinimumResults", 10)