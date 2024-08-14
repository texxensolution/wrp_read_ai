import os
import logging
import sys
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from ._configuration import Configuration
from src.services import GroqTranscriptionService
from typing import Dict
from src.interfaces import ITranscriber

load_dotenv('.env', override=True)

# initialize sqlalchemy

info_log_file = os.path.join("logs", "worker_info.log")
error_log_file = os.path.join("logs", "worker_error.log")

if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure the info file handler to log info and above
info_handler = RotatingFileHandler(
    info_log_file, 
    maxBytes=10 ** 6, 
    backupCount=5, 
    encoding='utf-8'
)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)

# Configure the error file handler to log only errors
error_handler = RotatingFileHandler(
    error_log_file, maxBytes=10 ** 6, backupCount=5, encoding='utf-8'
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(
    logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
)

# Configure the stream handler to log all levels to the console
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(
    logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[info_handler, error_handler, stream_handler]
)

config = Configuration(
    APP_ID=os.getenv('APP_ID'),
    APP_SECRET=os.getenv('APP_SECRET'),
    BITABLE_TOKEN=os.getenv('BITABLE_TOKEN'),
    BUBBLE_BEARER_TOKEN=os.getenv("BUBBLE_BEARER_TOKEN"),
    DEEPGRAM_TOKEN=os.getenv('DEEPGRAM_TOKEN'),
    HF_TOKEN=os.getenv('HF_TOKEN'),
    GROQ_API_KEY=os.getenv('GROQ_API_KEY'),
    VERSION=os.getenv('VERSION'),
    ENVIRONMENT=os.getenv('ENV'),
    NOTIFY_APP_ID=os.getenv("NOTIFY_APP_ID"),
    NOTIFY_APP_SECRET=os.getenv("NOTIFY_APP_SECRET")
)