from src.lark import Lark, BitableManager, FileManager
from src.interfaces import ITranscriber
from .config import config
from typing import Dict
from src.services import GroqTranscriptionService, \
    DeepgramTranscriptionService
from src.configs.config import groq_api_keys_manager

lark_client = Lark(
    app_id=config.APP_ID,
    app_secret=config.APP_SECRET,
    debug=True
)

notify_lark_client = Lark(
    app_id=config.NOTIFY_APP_ID,
    app_secret=config.NOTIFY_APP_SECRET
)

base_manager = BitableManager(
    lark_client=lark_client,
    bitable_token=config.BITABLE_TOKEN,
)

file_manager = FileManager(
    lark_client=lark_client,
    bitable_token=config.BITABLE_TOKEN
)

transcriptions_clients: Dict[str, ITranscriber] = {
    "groq": GroqTranscriptionService(
        api_manager=groq_api_keys_manager
    ),
    "deepgram": DeepgramTranscriptionService(
        token=config.DEEPGRAM_TOKEN
    )
}
