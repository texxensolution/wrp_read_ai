import logging
import os
from typing import List
from src.modules.lark import Lark, BitableManager, FileManager
from src.modules.common import LarkQueue, TaskQueue
from src.modules.services import TranscriptionService, ScriptExtractorService, VoiceAnalyzerService, LlamaService
from dataclasses import dataclass


@dataclass
class AppContext:
    def __init__(
        self,
        base_manager: BitableManager,
        file_manager: FileManager,
        transcription_service: TranscriptionService,
        script_extractor_service: ScriptExtractorService,
        voice_analyzer_service: VoiceAnalyzerService,
        llama_service: LlamaService,
        lark_queue: LarkQueue,
        logger: logging.Logger,
        task_queue: TaskQueue,
        sr_unprocessed_table_id: str = os.getenv('BUBBLE_TABLE_ID'),
        sr_processed_table_id: str = os.getenv('SCRIPT_READING_TABLE_ID'),
        server_task: List[str] = os.getenv('SERVER_TASK'),
        version: str = os.getenv('VERSION'),
        environment: str = os.getenv('ENV')
    ):
        self.base_manager: BitableManager = base_manager
        self.file_manager: FileManager = file_manager
        self.transcription_service: TranscriptionService = transcription_service
        self.script_extractor_service: ScriptExtractorService = script_extractor_service
        self.voice_analyzer_service: VoiceAnalyzerService = voice_analyzer_service
        self.llama_service: LlamaService = llama_service
        self.logger = logger
        self.server_task = server_task
        self.lark_queue: LarkQueue = lark_queue
        self.task_queue: TaskQueue = task_queue
        self.sr_unprocessed_table_id: str = sr_unprocessed_table_id
        self.sr_processed_table_id: str = sr_processed_table_id
        self.version: str = version
        self.environment: str = environment
    
    def __str__(self):
        return f"""
    base_manager: {self.base_manager}, 
    file_manager: {self.file_manager}, 
    transcription_service: {self.transcription_service}, 
    script_extractor_service: {self.script_extractor_service},
    voice_analyzer_service: {self.voice_analyzer_service},
    llama_service: {self.llama_service},
    version: {self.version},
    environment: {self.environment}
    """