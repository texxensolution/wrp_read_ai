import os
import logging
import sys
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from src.common import AppContext, LarkQueue, TaskQueue, Constants
from src.lark import BitableManager, FileManager, Lark
from src.services import LlamaService, OllamaService, ScriptExtractorService, TranscriptionService, \
    DeepgramTranscriptionService, VoiceAnalyzerService, ApplicantSubmittedRecordService, QuoteTranslationService, \
    PhotoInterpretationService
from src.services.QuoteTranslationService import QuoteTranslationService
from src.stores import Stores, ApplicantScriptReadingEvaluationStore, BubbleDataStore, \
    ApplicantQuoteTranslationEvaluationStore, ReferenceStore, ApplicantPhotoInterpretationEvaluationStore
from .Configuration import Configuration

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
    APP_CLI=os.getenv('APP_CLI'),
    APP_SECRET=os.getenv('APP_SECRET'),
)

lark_client = Lark(
    app_id=os.getenv('APP_ID'),
    app_secret=os.getenv('APP_SECRET')
)

BITABLE_TOKEN = os.getenv('BITABLE_TOKEN')
BUBBLE_TABLE_ID = os.getenv('BUBBLE_TABLE_ID')
SCRIPT_READING_TABLE_ID = os.getenv('SCRIPT_READING_TABLE_ID')
QUOTE_TRANSLATION_TABLE_ID = os.getenv('QUOTE_TRANSLATION_TABLE_ID')
PHOTO_INTERPRETATION_TABLE_ID = os.getenv('PHOTO_INTERPRETATION_TABLE_ID')
VERSION = os.getenv('VERSION')
environment = os.getenv('ENV')
SERVER_TASK = os.getenv('SERVER_TASK').split(',')
DEEPGRAM_TOKEN = os.getenv('DEEPGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
REFERENCE_TABLE_ID = os.getenv('REFERENCE_TABLE_ID')

base_manager = BitableManager(
    lark_client=lark_client,
    bitable_token=BITABLE_TOKEN,
)

file_manager = FileManager(
    lark_client=lark_client,
    bitable_token=BITABLE_TOKEN
)

stores = Stores(
    applicant_sr_evaluation_store=ApplicantScriptReadingEvaluationStore(
        table_id=SCRIPT_READING_TABLE_ID,
        base_manager=base_manager
    ),
    applicant_qt_evaluation_store=ApplicantQuoteTranslationEvaluationStore(
        table_id=QUOTE_TRANSLATION_TABLE_ID,
        base_manager=base_manager
    ),
    applicant_photo_evaluation_store=ApplicantPhotoInterpretationEvaluationStore(
        table_id=PHOTO_INTERPRETATION_TABLE_ID,
        base_manager=base_manager
    ),
    bubble_data_store=BubbleDataStore(
        table_id=BUBBLE_TABLE_ID,
        base_manager=base_manager
    ),
    reference_store=ReferenceStore(
        table_id=REFERENCE_TABLE_ID,
        base_manager=base_manager,
        logger=logging.getLogger()
    )
)

constants = Constants(
    UNPROCESSED_TABLE_ID=BUBBLE_TABLE_ID,
    SR_PROCESSED_TABLE_ID=SCRIPT_READING_TABLE_ID,
    REFERENCE_TABLE_ID=REFERENCE_TABLE_ID
)

ctx = AppContext(
    base_manager=base_manager,
    constants=constants,
    file_manager=file_manager,
    llama_service=LlamaService(
        client=OllamaService()
    ),
    lark_queue=LarkQueue(
        base_manager=base_manager,
        bitable_table_id=BUBBLE_TABLE_ID,
        environment=environment,
        version=VERSION,
    ),
    logger=logging.getLogger(),
    task_queue=TaskQueue(),
    script_extractor_service=ScriptExtractorService(version=VERSION),
    server_task=SERVER_TASK,
    environment=environment,
    version=VERSION,
    stores=stores,
    quote_translation_service=QuoteTranslationService(
        token=GROQ_API_KEY
    ),
    photo_interpretation_service=PhotoInterpretationService(token=GROQ_API_KEY),
    transcription_service=TranscriptionService(
        client=DeepgramTranscriptionService(token=DEEPGRAM_TOKEN)
    ),
    voice_analyzer_service=VoiceAnalyzerService(),
)
