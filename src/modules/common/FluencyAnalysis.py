from transformers import pipeline
from typing import List, Dict, Any

class FluencyAnalysis:
    def __init__(self):
        self.model = pipeline("audio-classification", model="megathil/fluency_prediction")
    
    
    def get_actual_prediction(self, items: List[Dict[str, Any]]):
        max_current = 0
        index = None
        for key, item in enumerate(items):
            score = item['score']
            if score > max_current:
                max_current = score
                index = key
        
        return items[index]
    
    def get_actual_scores(self, prediction) -> float:
        label = prediction['label']
        score = prediction['score']

        if label == 'Influent' or label == 'Very Influent':
            return 1 
        elif label == 'Average':
            return 3
        elif label == 'Fluent':
            return 5


    def analyze(self, audio_path: str) -> float:
        prediction = self.model(audio_path)

        highest_probability = self.get_actual_prediction(prediction)

        return self.get_actual_scores(highest_probability)






