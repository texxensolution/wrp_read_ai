from transformers import pipeline
import os

class VoiceAnalyzerService:
    def __init__(self) -> None:
        HF_TOKEN = os.getenv('HF_TOKEN')
        self.fluency_service = pipeline("audio-classification", model="jeromesky/consistency_accuracy_v1.0.3", token=HF_TOKEN)
        self.pronunciation_service = pipeline(model="jeromesky/pronunciation_accuracy_v1.0.3", task="audio-classification", token=HF_TOKEN)
    
    