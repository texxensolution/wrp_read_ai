from typing import Literal, Union
from pydantic import BaseModel
from os import getenv


class Configuration(BaseModel):
    APP_ID: Union[str, None] = getenv('APP_ID')
    APP_SECRET: Union[str, None] = getenv('APP_SECRET')
    BITABLE_TOKEN: Union[str, None] = getenv('BITABLE_TOKEN')
    BUBBLE_TABLE_ID: Union[str, None] = getenv('BUBBLE_TABLE_ID')
    BUBBLE_BEARER_TOKEN: Union[str, None] = getenv("BUBBLE_BEARER_TOKEN")
    SCRIPT_READING_TABLE_ID: Union[str, None] = getenv('SCRIPT_READING_TABLE_ID')
    QUOTE_TRANSLATION_TABLE_ID: Union[str, None] = getenv('QUOTE_TRANSLATION_TABLE_ID')
    PROCESSED_TABLE_ID: Union[str, None] = getenv('PROCESSED_TABLE_ID')
    PHOTO_INTERPRETATION_TABLE_ID: Union[str, None] = getenv('PHOTO_INTERPRETATION_TABLE_ID')
    REFERENCE_TABLE_ID: Union[str, None] = getenv('REFERENCE_TABLE_ID')
    DEEPGRAM_TOKEN: Union[str, None] = getenv('DEEPGRAM_TOKEN')
    HF_TOKEN: Union[str, None] = getenv('HF_TOKEN')
    GROQ_API_KEY: Union[str, None] = getenv('GROQ_API_KEY')
    VERSION: Union[str, None] = getenv('VERSION')
    ENVIRONMENT: Union[str, None] = getenv('ENV')
    SERVER_TASK: list[str] = getenv('SERVER_TASK')
    QUOTE_GROUP_CHAT_ID: Union[str, None] = getenv("QUOTE_GROUP_CHAT_ID")
    SR_GROUP_CHAT_ID: Union[str, None] = getenv("SR_GROUP_CHAT_ID")
    NOTIFY_APP_ID: Union[str, None] = getenv("NOTIFY_APP_ID")
    NOTIFY_APP_SECRET: Union[str, None] = getenv("NOTIFY_APP_SECRET")
    