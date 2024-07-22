class ReadingEvaluationService:
    def __init__(
        self, 
        transcriptionService: TranscriptionService,
        eloquentService: EloquentService,
        scriptExtractorService: ScriptExtractorService,
        fluencyAnalysisService: FluencyAnalysisService,
        pronunciationAnalyzerService: PronunciationAnalyzerService,
        ollamaService: Union[Ollama, None] = None,
        baseManager: BitableManager,
        fileManager: FileManager,

    ) -> None:
        self.transcriber: Transcriber
        self.eloquent: EloquentOpenAI
        self.base_manager: BitableManager
        self.file_manager: FileManager
        self.fluency_analysis: FluencyAnalysis
        self.pronunciation_analyzer: PronunciationAnalyzer
        self.script_extractor: ScriptExtractor
        self.ollama_client: Union[Ollama, None] = None
        self.destination_table_id: str = os.getenv('SCRIPT_READING_TABLE_ID'),