class EvaluationFailureError(Exception):
    def __init__(self, message="Evaluation failure!"):
        self.message = message
        super().__init__(f"Evaluation failure: message={self.message}")