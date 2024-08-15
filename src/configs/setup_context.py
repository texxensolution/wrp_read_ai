from src.common import AppContext, LarkQueue, TaskQueue
from src.services import GroqService, LlamaService, QuoteTranslationService, \
    ScriptReadingService, BubbleHTTPClientService, \
    TranscriptionService, VoiceAnalyzerService
from src.lark import LarkMessenger
from .config import config
from .setup_constants import base_constants
from .setup_services import base_manager, file_manager, \
    transcriptions_clients, notify_lark_client
from .setup_stores import stores
import logging
#

context = AppContext(
    base_manager=base_manager,
    file_manager=file_manager,
    llama_service=LlamaService(
        client=GroqService(
            token=config.GROQ_API_KEY
        )
    ),
    lark_queue=LarkQueue(
        base_manager=base_manager,
        bitable_table_id=base_constants.BUBBLE_TABLE_ID,
        environment=config.ENVIRONMENT,
        version=config.VERSION,
    ),
    lark_messenger=LarkMessenger(
        lark=notify_lark_client
    ),
    logger=logging.getLogger(),
    task_queue=TaskQueue(),
    environment=config.ENVIRONMENT,
    version=config.VERSION,
    stores=stores,
    quote_translation_service=QuoteTranslationService(
        token=config.GROQ_API_KEY
    ),
    script_reading_service=ScriptReadingService(
        token=config.GROQ_API_KEY
    ),
    bubble_http_client_service=BubbleHTTPClientService(
        config.BUBBLE_BEARER_TOKEN
    ),
    transcription_service=TranscriptionService(
        clients=transcriptions_clients
    ),
    voice_analyzer_service=VoiceAnalyzerService(),
)
