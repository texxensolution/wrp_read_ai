import json
import os
from pydantic import BaseModel, field_validator
from typing import List, Dict


class ScriptReadingResultDTO(BaseModel):
    name: str
    email: str
    transcription: str
    given_transcription: str
    script_id: str
    evaluation: str
    audio: List[Dict[str, str]]
    pronunciation: int
    fluency: int
    similarity_score: float
    voice_classification: float
    pacing_score: float
    wpm_category: int
    words_per_minute: float
    correct_word_count: int
    total_word_count: int
    audio_duration_seconds: float
    avg_pause_duration: float
    processing_duration: float
    parent_record_id: str
    version: str
    environment: str

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
        fluency: float,
        similarity_score: float,
        pronunciation: float,
        pacing_score: float,
        wpm_category: float,
        words_per_minute: float,
        audio_duration_seconds: float,
        avg_pause_duration: float,
        processing_duration: float,
        parent_record_id: str,
        version: str = os.getenv('VERSION'),
        environment: str = os.getenv('ENV')
    ):
        return ScriptReadingResultDTO(
            name=name,
            email=email,
            transcription=transcription,
            given_transcription=given_transcription,
            script_id=script_id,
            evaluation=evaluation,
            audio=audio,
            fluency=fluency,
            similarity_score=similarity_score,
            pronunciation=pronunciation,
            pacing_score=pacing_score,
            wpm_category=wpm_category,
            words_per_minute=words_per_minute,
            audio_duration_seconds=audio_duration_seconds,
            avg_pause_duration=avg_pause_duration,
            processing_duration=processing_duration,
            parent_record_id=parent_record_id,
            version=version,
            environment=environment
        ).dict()
