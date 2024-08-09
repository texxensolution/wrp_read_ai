import logging
import os
from typing import List
# update
from src.common._constants import Constants
from src.lark import Lark, BitableManager, FileManager, LarkMessenger
from src.common import LarkQueue, TaskQueue
from src.services import TranscriptionService, VoiceAnalyzerService, LlamaService, \
    QuoteTranslationService, PhotoInterpretationService, BubbleHTTPClientService, ScriptReadingService
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
        constants: Constants,
        stores: Stores,
        quote_translation_service: QuoteTranslationService,
        bubble_http_client_service: BubbleHTTPClientService,
        photo_interpretation_service: PhotoInterpretationService,
        script_reading_service: ScriptReadingService,
        server_task: List[str] = os.getenv('SERVER_TASK'),
        version: str = os.getenv('VERSION'),
        environment: str = os.getenv('ENV')
    ):
        self.base_manager: BitableManager = base_manager
        self.constants: Constants = constants
        self.file_manager: FileManager = file_manager
        self.lark_messenger: LarkMessenger = lark_messenger 
        self.transcription_service: TranscriptionService = transcription_service
        self.voice_analyzer_service: VoiceAnalyzerService = voice_analyzer_service
        self.llama_service: LlamaService = llama_service
        self.logger = logger
        self.server_task = server_task
        self.lark_queue: LarkQueue = lark_queue
        self.task_queue: TaskQueue = task_queue
        self.script_reading_service: ScriptReadingService = script_reading_service
        self.bubble_http_client_service: BubbleHTTPClientService = bubble_http_client_service
        self.quote_translation_service: QuoteTranslationService = quote_translation_service
        self.photo_interpretation_service: PhotoInterpretationService = photo_interpretation_service
        self.stores: Stores = stores
        self.version: str = version
        self.environment: str = environment
