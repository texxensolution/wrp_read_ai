from pydantic import BaseModel, field_validator
from typing import Dict, List


class PhotoInterpretationResultDTO(BaseModel):
    parent_record_id: str
    name: str
    email: str
    audio: List[Dict[str, str]]
    description: str
    evaluation: str
    transcription: str
    analytical_thinking: int
    originality: int
    language: int
    organization: int
    support: int
    focus_point: int
    version: str
    environment: str
    processing_time: float

    @field_validator('audio', mode="before")
    def format_audio(cls, v):
        if isinstance(v, str):
            return [{"file_token": v}]
        return v