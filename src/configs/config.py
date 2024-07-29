import os
import logging
import sys
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from src.common import AppContext, LarkQueue, TaskQueue, Constants
from src.lark import BitableManager, FileManager, Lark
from src.services import GroqService, LlamaService, OllamaService, ScriptExtractorService, TranscriptionService, \
    DeepgramTranscriptionService, VoiceAnalyzerService, QuoteTranslationService, \
    PhotoInterpretationService
from src.services.QuoteTranslationService import QuoteTranslationService
from src.stores import Stores, ApplicantScriptReadingEvaluationStore, BubbleDataStore, \
    ApplicantQuoteTranslationEvaluationStore, ReferenceStore, ApplicantPhotoInterpretationEvaluationStore
from .Configuration import Configuration
from src.services import GroqTranscriptionService
from typing import Dict
from src.interfaces import ITranscriber

load_dotenv('.env')

info_log_file = os.path.join("logs", "worker_info.log")
error_log_file = os.path.join("logs", "worker_error.log")

if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure the info file handler to log info and above
info_handler = RotatingFileHandler(info_log_file, maxBytes=10 ** 6, backupCount=5, encoding='utf-8')
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Configure the error file handler to log only errors
error_handler = RotatingFileHandler(error_log_file, maxBytes=10 ** 6, backupCount=5, encoding='utf-8')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Configure the stream handler to log all levels to the console
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[info_handler, error_handler, stream_handler]
)

config = Configuration(
    BITABLE_TOKEN=os.getenv('BITABLE_TOKEN'),
    BUBBLE_TABLE_ID=os.getenv('BUBBLE_TABLE_ID'),
    SCRIPT_READING_TABLE_ID=os.getenv('SCRIPT_READING_TABLE_ID'),
    QUOTE_TRANSLATION_TABLE_ID=os.getenv('QUOTE_TRANSLATION_TABLE_ID'),
    PHOTO_INTERPRETATION_TABLE_ID=os.getenv('PHOTO_INTERPRETATION_TABLE_ID'),
    VERSION=os.getenv('VERSION'),
    ENVIRONMENT=os.getenv('ENV'),
    APP_ID=os.getenv('APP_ID'),
    APP_SECRET=os.getenv('APP_SECRET'),
    DEEPGRAM_TOKEN=os.getenv('DEEPGRAM_TOKEN'),
    GROQ_API_KEY=os.getenv('GROQ_API_KEY'),
    HF_TOKEN=os.getenv('HF_TOKEN'),
    REFERENCE_TABLE_ID=os.getenv('REFERENCE_TABLE_ID'),
    PROCESSED_TABLE_ID=os.getenv('PROCESSED_TABLE_ID'),
    SERVER_TASK=os.getenv('SERVER_TASK').split(','),
)

lark_client = Lark(
    app_id=config.APP_ID,
    app_secret=config.APP_SECRET
)

base_manager = BitableManager(
    lark_client=lark_client,
    bitable_token=config.BITABLE_TOKEN,
)

file_manager = FileManager(
    lark_client=lark_client,
    bitable_token=config.BITABLE_TOKEN
)

stores = Stores(
    applicant_sr_evaluation_store=ApplicantScriptReadingEvaluationStore(
        table_id=config.SCRIPT_READING_TABLE_ID,
        base_manager=base_manager
    ),
    applicant_qt_evaluation_store=ApplicantQuoteTranslationEvaluationStore(
        table_id=config.QUOTE_TRANSLATION_TABLE_ID,
        base_manager=base_manager
    ),
    applicant_photo_evaluation_store=ApplicantPhotoInterpretationEvaluationStore(
        table_id=config.PHOTO_INTERPRETATION_TABLE_ID,
        base_manager=base_manager
    ),
    bubble_data_store=BubbleDataStore(
        table_id=config.BUBBLE_TABLE_ID,
        base_manager=base_manager
    ),
    reference_store=ReferenceStore(
        table_id=config.REFERENCE_TABLE_ID,
        base_manager=base_manager,
        logger=logging.getLogger()
    )
)

constants = Constants(
    UNPROCESSED_TABLE_ID=config.BUBBLE_TABLE_ID,
    SR_PROCESSED_TABLE_ID=config.SCRIPT_READING_TABLE_ID,
    REFERENCE_TABLE_ID=config.REFERENCE_TABLE_ID
)

transcriptions_clients: Dict[str, ITranscriber] = {
    "groq": GroqTranscriptionService(token=config.GROQ_API_KEY),
    "deepgram": DeepgramTranscriptionService(token=config.DEEPGRAM_TOKEN)
}


context = AppContext(
    base_manager=base_manager,
    constants=constants,
    file_manager=file_manager,
    llama_service=LlamaService(
        client=GroqService(token=config.GROQ_API_KEY)
    ),
    lark_queue=LarkQueue(
        base_manager=base_manager,
        bitable_table_id=config.BUBBLE_TABLE_ID,
        environment=config.ENVIRONMENT,
        version=config.VERSION,
    ),
    logger=logging.getLogger(),
    task_queue=TaskQueue(),
    script_extractor_service=ScriptExtractorService(version=config.VERSION),
    server_task=config.SERVER_TASK,
    environment=config.ENVIRONMENT,
    version=config.VERSION,
    stores=stores,
    quote_translation_service=QuoteTranslationService(
        token=config.GROQ_API_KEY
    ),
    photo_interpretation_service=PhotoInterpretationService(token=config.GROQ_API_KEY),
    transcription_service=TranscriptionService(
        clients=transcriptions_clients
    ),
    voice_analyzer_service=VoiceAnalyzerService(),
)
