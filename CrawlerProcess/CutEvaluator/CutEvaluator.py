class CutEvaluator:

    def __init__(self, stop_criteria):
        self.stop_criteria = stop_criteria

    def should_continue(self, errors: int) -> bool:

        if self._maximum_errors_reached(errors):
            return False

        return True

    def _maximum_errors_reached(self, errors: int) -> bool:
        return errors >= self.stop_criteria.maximum_errors
