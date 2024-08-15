from src.stores import Stores, LarkDataStore, BubbleDataStore, ReferenceStore
from src.dtos import ScriptReadingResultDTO, QuoteTranslationResultDTO
from .setup_services import base_manager
from .setup_constants import base_constants
from .config import config
import logging

stores = Stores(
    sr_eval_store=LarkDataStore[ScriptReadingResultDTO](
        base_manager=base_manager,
        table_id=base_constants.SCRIPT_READING_TABLE_ID
    ),
    qt_eval_store=LarkDataStore[QuoteTranslationResultDTO](
        base_manager=base_manager,
        table_id=base_constants.QUOTE_TRANSLATION_TABLE_ID
    ),
    bubble_data_store=BubbleDataStore(
        base_manager=base_manager,
        table_id=base_constants.BUBBLE_TABLE_ID,
    ),
    reference_store=ReferenceStore(
        base_manager=base_manager,
        table_id=base_constants.REFERENCE_TABLE_ID,
        logger=logging.getLogger("reference_store"),
        version=config.VERSION
    )
)