import os
from ._base_constants import BaseConstants

base_constants = BaseConstants(
    REFERENCE_TABLE_ID=os.getenv("REFERENCE_TABLE_ID"),
    LOGS_TABLE_ID=os.getenv("LOGS_TABLE_ID"),
    SR_GROUP_CHAT_ID=os.getenv("SR_GROUP_CHAT_ID"),
    SCRIPT_READING_TABLE_ID=os.getenv("SCRIPT_READING_TABLE_ID"),
    QUOTE_GROUP_CHAT_ID=os.getenv("QUOTE_GROUP_CHAT_ID"),
    BUBBLE_TABLE_ID=os.getenv("BUBBLE_TABLE_ID"),
    QUOTE_TRANSLATION_TABLE_ID=os.getenv("QUOTE_TRANSLATION_TABLE_ID")
)