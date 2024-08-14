from pydantic import BaseModel


class BaseConstants(BaseModel):
    REFERENCE_TABLE_ID: str
    LOGS_TABLE_ID: str
    SR_GROUP_CHAT_ID: str
    QUOTE_GROUP_CHAT_ID: str
    SCRIPT_READING_TABLE_ID: str
    QUOTE_TRANSLATION_TABLE_ID: str
    BUBBLE_TABLE_ID: str