from pydantic import BaseModel

from src.stores import ApplicantScriptReadingEvaluationStore, BubbleDataStore, ApplicantQuoteTranslationEvaluationStore


class Stores:
    def __init__(
            self,
            applicant_sr_evaluation_store: ApplicantScriptReadingEvaluationStore,
            applicant_qt_evaluation_store: ApplicantQuoteTranslationEvaluationStore,
            bubble_data_store: BubbleDataStore
    ):
        self.applicant_sr_evaluation_store: ApplicantScriptReadingEvaluationStore = applicant_sr_evaluation_store
        self.applicant_qt_evaluation_store: ApplicantQuoteTranslationEvaluationStore = applicant_qt_evaluation_store
        self.bubble_data_store: BubbleDataStore = bubble_data_store
