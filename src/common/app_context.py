import logging
import os
from src.lark import BitableManager, FileManager, LarkMessenger
from src.common import LarkQueue, TaskQueue
from src.services import TranscriptionService, VoiceAnalyzerService, \
    LlamaService, QuoteTranslationService, \
    BubbleHTTPClientService, ScriptReadingService
from dataclasses import dataclass
from src.stores import Stores


@dataclass
class AppContext:
    def __init__(
        self,
        base_manager: BitableManager,
        file_manager: FileManager,
        lark_messenger: LarkMessenger,
        transcription_service: TranscriptionService,
        voice_analyzer_service: VoiceAnalyzerService,
        llama_service: LlamaService,
        lark_queue: LarkQueue,
        logger: logging.Logger,
        task_queue: TaskQueue,
        stores: Stores,
        quote_translation_service: QuoteTranslationService,
        bubble_http_client_service: BubbleHTTPClientService,
        script_reading_service: ScriptReadingService,
        version: str = os.getenv('VERSION'),
        environment: str = os.getenv('ENV')
    ):
        self.base_manager = base_manager
        self.file_manager = file_manager
        self.lark_messenger = lark_messenger
        self.transcription_service = transcription_service
        self.voice_analyzer_service = voice_analyzer_service
        self.llama_service = llama_service
        self.logger = logger
        self.lark_queue = lark_queue
        self.task_queue = task_queue
        self.script_reading_service = script_reading_service
        self.bubble_http_client_service = bubble_http_client_service
        self.quote_translation_service = quote_translation_service
        self.stores = stores
        self.version = version
        self.environment = environment
