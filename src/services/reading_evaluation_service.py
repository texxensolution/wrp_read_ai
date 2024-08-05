import os
from src.interfaces import ITranscriber
from .transcription_service import TranscriptionService
from .voice_analyzer_service import VoiceAnalyzerService
from .llama_service import LlamaService
from src.lark import BitableManager, FileManager

class ReadingEvaluationService:
    def __init__(
        self, 
        transcription_service: ITranscriber, 
        base_manager: BitableManager, 
        file_manager: FileManager,
        voice_analyzer_service: VoiceAnalyzerService,
        llama_service: LlamaService,
        destination_table_id: str = os.getenv('PROCESSED_TABLE_ID')
    ):
        self.transcription_service: TranscriptionService = transcription_service
        self.base_manager: BitableManager = base_manager 
        self.file_manager: FileManager = file_manager 
        self.voice_analyzer_service: VoiceAnalyzerService = voice_analyzer_service
        self.llama_service: LlamaService = llama_service
        self.destination_table_id: str = destination_table_id