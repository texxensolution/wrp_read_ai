import os

from pydantic import BaseModel


class Constants(BaseModel):
    SR_PROCESSED_TABLE_ID: str = os.getenv('SCRIPT_READING_TABLE_ID')
    UNPROCESSED_TABLE_ID: str = os.getenv('BUBBLE_TABLE_ID')