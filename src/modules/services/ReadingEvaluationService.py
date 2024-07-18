import os
from src.modules.interfaces import ITranscriber
from .TranscriptionService import TranscriptionService
from .VoiceAnalyzerService import VoiceAnalyzerService
from .ScriptExtractorService import ScriptExtractorService
from .LlamaService import LlamaService
from src.modules.lark import BitableManager, FileManager

class ReadingEvaluationService:
    def __init__(
        self, 
        transcription_service: ITranscriber, 
        base_manager: BitableManager, 
        file_manager: FileManager,
        voice_analyzer_service: VoiceAnalyzerService,
        script_extractor_service: ScriptExtractorService,
        llama_service: LlamaService,
        destination_table_id: str = os.getenv('PROCESSED_TABLE_ID')
    ):
        self.transcription_service: TranscriptionService = transcription_service
        self.base_manager: BitableManager = base_manager 
        self.file_manager: FileManager = file_manager 
        self.voice_analyzer_service: VoiceAnalyzerService = voice_analyzer_service
        self.script_extractor: ScriptExtractorService = script_extractor_service
        self.llama_service: LlamaService = llama_service
        self.destination_table_id: str = destination_table_id