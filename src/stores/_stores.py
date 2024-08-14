from .lark_data_store import LarkDataStore
from src.dtos import QuoteTranslationResultDTO, ScriptReadingResultDTO
from src.stores import BubbleDataStore, \
    ReferenceStore


class Stores:
    def __init__(
        self,
        sr_eval_store: LarkDataStore[ScriptReadingResultDTO],
        qt_eval_store: LarkDataStore[QuoteTranslationResultDTO],
        bubble_data_store: BubbleDataStore,
        reference_store: ReferenceStore
    ):
        self.sr_eval_store = sr_eval_store
        self.qt_eval_store = qt_eval_store
        self.bubble_data_store: BubbleDataStore = bubble_data_store
        self.reference_store: ReferenceStore = reference_store
