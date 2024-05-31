from dataclasses import dataclass
from typing import List, Any, Dict

@dataclass
class ScriptReadingPayloadBuilder:
    builded_payload = {}

    def make(self, record: List[Dict[str, Any]], evaluation: List[Dict[str, Any]]):
        self.builded_payload = {
            "email": record["email"],
            'name': record['name'],
            "result": evaluation['result'],
            'audio_duration_seconds': evaluation['audio_duration'],
            'words_per_minute': evaluation['words_per_minute'],
            'transcription': evaluation['transcription'],
            'given_transcription': evaluation['given_transcription'],
            'energy': float(evaluation['energy']),
            'pronunciation': evaluation['score_object']['pronunciation'],
            'enunciation': evaluation['score_object']['enunciation'],
            'clarityofexpression': evaluation['score_object']['clarityofexpression'],
            'similarity_score': evaluation['similarity_score'],
            'evaluation': evaluation['evaluation'],
            'metadata': evaluation['metadata'],
            'parent_record_id': record['record_id'],
            'wpm_category': evaluation['wpm_category']
        }

        return self
    
    def attach_file_token(self, key: str, file_token: str):
        self.builded_payload[key] = [{ "file_token": file_token }]
        return self
    
    def build(self) -> str:
        created_payload = self.builded_payload

        self.builded_payload = {}

        return created_payload
    