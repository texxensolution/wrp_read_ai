import json
import os
from pydantic import BaseModel, field_validator
from typing import List, Dict


class EnhancedScriptReadingResultDTO(BaseModel):
    name: str
    email: str
    transcription: str
    given_transcription: str
    script_id: str
    evaluation: str
    audio: List[Dict[str, str]]
    correct_word_count: int
    total_word_count: int
    parent_record_id: str
    version: str
    environment: str
    similarity_score: float


    @field_validator('audio', mode="before")
    def format_audio(cls, v):
        """
        format the audio field to list of dictionary with `file_token` as its key
        """
        if isinstance(v, str):
            return [{"file_token": v}]
        return v

    def to_json(self):
        """
        Format to lark compatible format
        """
        return json.dumps({
            "fields": self.model_dump()
        })

    @staticmethod
    def transform_to_dict(
        name: str,
        email: str,
        transcription: str,
        given_transcription: str,
        script_id: str,
        evaluation: str,
        audio: str,
        parent_record_id: str,
        version: str = os.getenv('VERSION'),
        environment: str = os.getenv('ENV')
    ):
        return EnhancedScriptReadingResultDTO(
            name=name,
            email=email,
            transcription=transcription,
            given_transcription=given_transcription,
            script_id=script_id,
            evaluation=evaluation,
            audio=audio,
            parent_record_id=parent_record_id,
            version=version,
            environment=environment
        ).dict()
