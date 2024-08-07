from pydantic import BaseModel, field_validator
from typing import Dict, List, Union

AudioFieldType = Union[str, List[Dict[str, str]]]

class QuoteTranslationResultDTO(BaseModel):
    parent_record_id: str
    name: str
    email: str
    audio: AudioFieldType
    quote: str
    evaluation: str
    transcription: str
    version: str
    environment: str
    processing_time: float
    understanding: int
    personal_connection: int
    insightfulness: int
    practical_application: int
    no_of_retries: int = 0

    @field_validator('audio', mode="before")
    def format_audio(cls, v: AudioFieldType):
        if isinstance(v, str):
            return [{"file_token": v}]
        return v