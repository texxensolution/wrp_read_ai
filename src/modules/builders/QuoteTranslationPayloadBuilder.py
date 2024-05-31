from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class QuoteTranslationPayloadBuilder:
    builded_payload = {}

    def make(self, record: List[Dict[str, Any]], evaluation: List[Dict[str, Any]]):
        self.builded_payload = {
            "email": record["email"],
            "result": evaluation['result'],
            "transcription": evaluation["transcription"],
            "quote": evaluation["quote"],
            "understanding_of_the_quote": evaluation["understanding_of_the_quote"],
            "relevance_to_the_question": evaluation["relevance_to_the_question"],
            "depth_of_analysis": evaluation["depth_of_analysis"],
            "support_and_justification": evaluation["support_and_justification"],
            "original_and_creativity": evaluation["original_and_creativity"]
        }

        return self

    
    def attach_file_token(self, key: str, file_token: str):
        self.builded_payload[key] = [{ "file_token": file_token }]

        return self

    def build(self):
        created_payload = self.builded_payload

        self.builded_payload = {}
        
        return created_payload


