from dataclasses import dataclass
from typing import List, Any, Dict

@dataclass
class LarkPayloadBuilder:
    builded_payload = {}
    
    def __init__(self):
        self.payload = {}

    def add_key_value(self, key: str, value: str):
        self.payload[key] = value
        return self

    def attach_media_file_token(self, key: str, value: str):
        self.payload[key] = [{"file_token": value}]
        return self
    
    def build(self) -> dict:
        return self.payload

    @staticmethod
    def builder():
        return LarkPayloadBuilder()