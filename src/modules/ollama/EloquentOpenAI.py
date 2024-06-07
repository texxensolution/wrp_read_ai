import numpy as np
import librosa
import os
import re
import Levenshtein
import openai
import json
import math
import joblib
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

    def quote_translation_prompt(self, speaker_transcript: str, quote: str):
        return f"""
            Instruction:
            Language: Can be tagalog or english
            Evaluate the speaker answer on how he/she interpret the given quote below and include the scores in json format output and brief description on how you evaluate the criterias
            Json Object: understanding_of_the_quote, relevance_to_the_question, depth_of_analysis, support_and_justification, original_and_creativity

            
            Condition: If the applicant interpretation just repeated the given quote give only 1 point to all criterias

            Criterias:
                Understanding of the quote: (average 5 points)
                - Clarity: Assess if the applicant clearly understand the meaning of the quote. 
                - Accuracy: Is the applicant interpretation accurate and faithful to the original context of the quote.

                Relevance to the Question: (average 5 points)
                - Contextual Fit: How well does the applicant interpretation fit within the context of the question asked? 
                - Applicability: Is the applicant interpretation relevant to the broader topic or issue being discussed? 

                Depth of Analysis (average 5 points)
                - Insight: Does the applicant provide insightful analysis and go beyond a surface-level interpretation?
                - Nuance: Are the complexities and subtleties of the quote explored?

                Support and Justification (average 5 points)
                - Evidence: Does the applicant support their interpretation with evidence or examples?
                - Reasoning: Is the interpretation logically justified and well-argued?

                Originality and Creativity (average 5 points)
                - Original Thought: Does the applicant bring original ideas or perspectives to their interpretation?
                - Creativity: Is the interpretation creative and engaging?

            Quote: {quote} \n
            Interpretation: {speaker_transcript}
        """
    
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
        return self.openai.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {
                    'role': 'system',
                    'content': combined_prompt_answer
                }
            ],
        ).choices[0].message.content
    
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

    def script_reading_evaluation(self, given_script: str, transcription: str, audio_path: str):
        y, sr = librosa.load(audio_path)
        avg_pause_duration = self.calculate_pause_duration(y, sr)
        audio_duration = librosa.get_duration(y=y, sr=sr)
        processed_transcription = TextPreprocessor.normalize(transcription)
        given_script = TextPreprocessor.normalize_text_with_new_lines(given_script)
        words_per_minute = AudioProcessor.calculate_words_per_minute(processed_transcription, audio_duration)
        similarity_score = TranscriptionProcessor.compute_distance(
            given_script=given_script, 
            transcription=transcription
        )
        pitch_std = FeatureExtractor.load_audio(y, sr).pitch_consistency()
        pitch_consistency = AudioProcessor.determine_pitch_consistency(pitch_std)
        prompt = self.generate_prompt(
            speaker_transcript=transcription, 
            given_transcript=given_script
        )
        result = self.evaluate(prompt)
        captured_json_result = TextPreprocessor.get_json_from_text(result)
        evaluation = TextPreprocessor.remove_json_object_from_texts(result)
        wpm_category = AudioProcessor.determine_wpm_category(words_per_minute)
        classification = self.audio_classifier.predict(y, sr)

        scores = {
            "result": result,
            "avg_pause_duration": str(avg_pause_duration),
            "audio_duration": audio_duration,
            "words_per_minute": words_per_minute,
            "transcription": processed_transcription,
            "given_transcription": given_script,
            "similarity_score": similarity_score,
            "score_object": captured_json_result,
            "evaluation": evaluation.strip(),
            "audio_path": audio_path,
            "wpm_category": wpm_category,
            "classification": classification,
            "pitch_consistency": pitch_consistency
        }

        return scores

