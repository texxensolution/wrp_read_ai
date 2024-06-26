class EvaluationFailureError(Exception):
    def __init__(self, message="Evaluation failure!"):
        self.message = message
        super().__init__(self.message)