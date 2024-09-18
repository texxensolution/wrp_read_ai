from src.common import AppContext, LarkQueue, TaskQueue
from src.configs.config import groq_api_keys_manager
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

context = AppContext(
    base_manager=base_manager,
    file_manager=file_manager,
    llama_service=LlamaService(
        client=GroqService(
            api_manager=groq_api_keys_manager
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
        api_manager=groq_api_keys_manager
    ),
    script_reading_service=ScriptReadingService(
        api_manager=groq_api_keys_manager
    ),
    bubble_http_client_service=BubbleHTTPClientService(
        config.BUBBLE_BEARER_TOKEN
    ),
    transcription_service=TranscriptionService(
        clients=transcriptions_clients
    ),
    voice_analyzer_service=VoiceAnalyzerService(),
)
