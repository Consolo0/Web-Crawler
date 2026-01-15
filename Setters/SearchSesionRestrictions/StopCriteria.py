class StopCriteria:
    def __init__(self, stop_criteria_params: dict = None):
        if stop_criteria_params is None:
            stop_criteria_params = {}
        self._maximum_errors = stop_criteria_params.get("maximum_errors", 5)
        self._timeout = stop_criteria_params.get("timeout", 3600)
        self._minimum_results = stop_criteria_params.get("minimum_results", 10)

    @property
    def maximum_errors(self) -> int:
        return self._maximum_errors
    @property
    def timeout(self) -> int:
        return self._timeout
    @property
    def minimum_results(self) -> int:
        return self._minimum_results
