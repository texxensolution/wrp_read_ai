from pydantic import BaseModel

from src.stores import ApplicantScriptReadingEvaluationStore, BubbleDataStore


class Stores:
    def __init__(
            self,
            applicant_sr_evaluation_store: ApplicantScriptReadingEvaluationStore,
            bubble_data_store: BubbleDataStore
    ):
        self.applicant_sr_evaluation_store: ApplicantScriptReadingEvaluationStore = applicant_sr_evaluation_store
        self.bubble_data_store: BubbleDataStore = bubble_data_store
