class StopCriteria:
    def __init__(self, stop_criteria_params: dict = None):
        if stop_criteria_params is None:
            stop_criteria_params = {}
        self._maximum_errors = stop_criteria_params.get("maximum_errors", 5)

    @property
    def maximum_errors(self) -> int:
        return self._maximum_errors
