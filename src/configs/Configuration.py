from typing import Literal, Union
from pydantic import BaseModel
from os import getenv


class Configuration(BaseModel):
    APP_CLI: Union[str, None] = getenv('APP_CLI')
    APP_SECRET: Union[str, None] = getenv('APP_SECRET')
    BITABLE_TOKEN: Union[str, None] = getenv('BITABLE_TOKEN')
    BUBBLE_TABLE_ID: Union[str, None] = getenv('BUBBLE_TABLE_ID')
    SCRIPT_READING_TABLE_ID: Union[str, None] = getenv('SCRIPT_READING_TABLE_ID')
    QUOTE_TRANSLATION_TABLE_ID: Union[str, None] = getenv('QUOTE_TRANSLATION_TABLE_ID')
    PROCESSED_TABLE_ID: Union[str, None] = getenv('PROCESSED_TABLE_ID')
    PHOTO_INTERPRETATION_TABLE_ID: Union[str, None] = getenv('PHOTO_INTERPRETATION_TABLE_ID')
    DEEPGRAM_TOKEN: Union[str, None] = getenv('DEEPGRAM_TOKEN')
    HF_TOKEN: Union[str, None] = getenv('HF_TOKEN')
    VERSION: Union[str, None] = getenv('VERSION')
    ENVIRONMENT: Union[str, None] = getenv('ENV')
    SERVER_TASK: Union[str, None] = getenv('SERVER_TASK')

