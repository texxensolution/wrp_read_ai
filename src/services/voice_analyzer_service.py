from transformers import pipeline
import os

class VoiceAnalyzerService:
    def __init__(self):
        token = os.getenv('HF_TOKEN')
        self.pronunciation_analyzer = pipeline(model="jeromesky/pronunciation_accuracy_v1.0.3", task="audio-classification", token=token)
        self.fluency_analyzer = pipeline("audio-classification", model="jeromesky/consistency_accuracy_v1.0.3", token=token)
        self.voice_classification_analyzer = pipeline(model='models/pronunciation_v3', task="audio-classification")

    def calculate_score(self, input_path: str):
        pronunciation_scores = self.pronunciation_analyzer(input_path)
        fluency_scores = self.fluency_analyzer(input_path)
        voice_classification_scores = self.voice_classification_analyzer(input_path)

        pronunciation_max_score_label = max(pronunciation_scores, key=lambda x: x['score'])['label']
        fluency_max_score_label = max(fluency_scores, key=lambda x: x['score'])['label']
        voice_classification_label = max(voice_classification_scores, key=lambda x: x['score'])['label']

        if pronunciation_max_score_label == 'Poor':
            pronunciation = 1
        elif pronunciation_max_score_label == 'Average':
            pronunciation = 3
        elif pronunciation_max_score_label == 'Excellent':
            pronunciation = 5
        else:
            pronunciation = 1

        if fluency_max_score_label == 'Influent':
            fluency = 1 
        elif fluency_max_score_label == 'Average':
            fluency = 3
        elif fluency_max_score_label == 'Fluent':
            fluency = 5
        else:
            fluency = 1

        if voice_classification_label == 'Good':
            voice_classification = 5
        else:
            voice_classification = 1
        
        return pronunciation, fluency, voice_classification

            