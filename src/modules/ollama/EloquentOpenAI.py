import numpy as np
import librosa
import os
import re
import Levenshtein
import openai
import json
import math
import joblib
from tokencost import calculate_prompt_cost
from .Ollama import Ollama
from pydub import AudioSegment
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.modules.common import FeatureExtractor, TextPreprocessor, TranscriptionProcessor, AudioProcessor

class EloquentOpenAI:
    def __init__(self, model = 'gpt-3.5-turbo', classifier_path: str = "classifier.joblib"):
        self.openai_key = os.getenv('OPENAI2_KEY')
        self.fillers = ['ay', 'ah', 'eh', 'ano', 'um', 'uhm']
        self.joined_fillers = ", ".join(self.fillers)
        self.openai = openai.OpenAI(api_key=self.openai_key)

    def generate_prompt(self, speaker_transcript: str, given_transcript: str):
        return f"""
            Instruction:
            Language: Tagalog, English
            Evaluate the transcription based on the criteria below and include the scores in json format output and brief description on how you evaluate the criterias
            Json Object: pronunciation, enunciation, clarityofexpression, grammarandsyntax

            Criterias:
                    - Pronunciation: Assess the accuracy of word pronunciations according to standard language conventions. Provide a score from 1 (poor) to 5 (excellent).
                    - Enunciation: Evaluate the clarity and precision in articulating individual sounds and words. Assign a score from 1 (unclear) to 5 (crystal clear).
                    - Clarity of Expression: Assess how clearly the participant communicates ideas and concepts, avoiding ambiguity or confusion. Provide a score from 1 (unclear) to 5 (crystal clear).
                    - Grammar and Syntax: Evaluate the correctness of the participant's grammar and sentence structure. Provide a score from 1 (poor) to 5 (excellent).
                    - Compare the two Speaker Transcription and Given Script

            Penalty System:
                - Fillers: [{self.joined_fillers}]\n\n

            Speaker Transcription: {speaker_transcript}
            Given Script: {given_transcript}
        """
    
    def evaluate(self, combined_prompt_answer: str):
        prompt=[
                {
                    'role': 'system',
                    'content': combined_prompt_answer
                }
            ]
        cost = self.calculate_ai_cost(prompt)
        return self.openai.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=prompt,
        ).choices[0].message.content, cost 

    def calculate_ai_cost(self, prompt):
        return float(calculate_prompt_cost(prompt, 'gpt-3.5-turbo'))

    
    def evaluate_quote_translation(self, quote: str, transcription: str):
        combined_prompt_answer = self.quote_translation_prompt(transcription, quote)
        result = self.evaluate(combined_prompt_answer)
        score_object = self.capture_json_result(result)
        scores = {}

        for key, value in score_object.items():
            scores[key] = value

        scores["result"] = result
        scores["evaluation"] = self.remove_json_object_from_text(result)
        scores["transcription"] = transcription
        scores["quote"] = quote

        return scores
