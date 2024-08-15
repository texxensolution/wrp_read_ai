from typing import Literal, Union
from pydantic import BaseModel
from os import getenv


class Configuration(BaseModel):
    APP_ID: Union[str, None] = getenv('APP_ID')
    APP_SECRET: Union[str, None] = getenv('APP_SECRET')
    BITABLE_TOKEN: Union[str, None] = getenv('BITABLE_TOKEN')
    BUBBLE_BEARER_TOKEN: Union[str, None] = getenv("BUBBLE_BEARER_TOKEN")
    DEEPGRAM_TOKEN: Union[str, None] = getenv('DEEPGRAM_TOKEN')
    HF_TOKEN: Union[str, None] = getenv('HF_TOKEN')
    GROQ_API_KEY: Union[str, None] = getenv('GROQ_API_KEY')
    VERSION: Union[str, None] = getenv('VERSION')
    ENVIRONMENT: Union[str, None] = getenv('ENV')
    NOTIFY_APP_ID: Union[str, None] = getenv("NOTIFY_APP_ID")
    NOTIFY_APP_SECRET: Union[str, None] = getenv("NOTIFY_APP_SECRET")