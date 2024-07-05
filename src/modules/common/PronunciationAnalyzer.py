from transformers import pipeline
import os

class PronunciationAnalyzer:
    def __init__(self):
        self.model = pipeline(model="jeromesky/pronunciation_accuracy", task="audio-classification", token=os.getenv('HF_TOKEN'))

    def predict(self, input_path: str):
        scores = self.model(input_path)

        max_score_label = max(scores, key=lambda x: x['score'])['label']

        if max_score_label == 'Poor':
            return 1
        elif max_score_label == 'Average':
            return 3
        elif max_score_label == 'Excellent':
            return 5
