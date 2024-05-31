from .Ollama import Ollama
from pydub import AudioSegment
import numpy as np
import librosa
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein
import openai
import json
import math
from src.modules.enums import AssessmentType
from src.modules.whisper import FeatureExtractor

class EloquentOpenAI:
    def __init__(self, model = 'gpt-3.5-turbo'):
        self.openai_key = os.getenv('OPENAI2_KEY')
        self.fillers = ['ay', 'ah', 'eh', 'ano', 'um', 'uhm']
        self.joined_fillers = ", ".join(self.fillers)
        self.openai = openai.OpenAI(api_key=self.openai_key)

    def quote_translation_prompt(self, speaker_transcript: str, quote: str):
        print('transcript', speaker_transcript)
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
    
    def aggregate_scores(self, scores=[]):
        evaluated_scores = "\n\n".join(scores)

        combined_prompt = self.ollama.combine_prompt_and_message(self.aggregate_score_prompt, evaluated_scores)

        return self.ollama.generate(combined_prompt)

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
    
    def normalize_transcription(self, transcription: str):
        transcripts = []
        lines = transcription.split('\n')
        # timestamp, transcript = transcription.split(' : : ')
        for line in lines:
            timestamp, transcript = line.split(': :')
            transcript = transcript.strip()
            transcripts.append(transcript)
        return self.preprocess(" ".join(transcripts).lower())
    
    def normalize_given_transcription(self, transcription: str):
        transcripts = []
        lines = transcription.split('\n')

        for line in lines:
            transcript = line.strip()
            transcripts.append(transcript)

        return self.preprocess(" ".join(transcripts).lower())
    
    def capture_text_from_result(self, result: str):
        start_index, end_index = result.find('{'), result.find('}') + 1 
        evaluation = result[end_index:]
        return evaluation

    def calculate_words_per_minute(self, transcription: str, duration_sec):
        return len(transcription.split(' ')) / (duration_sec / 60) # convert duration to minute
    
    def capture_json_result(self, result: str):
        start_index, end_index = result.find('{'), result.find('}') + 1 

        json_data = result[start_index:end_index]

        return json.loads(json_data)
    
    def remove_json_object_from_text(self, text: str):
        start_index, end_index = text.find('{'), text.find('}') + 1

        new_text = text[:start_index] + text[end_index:]

        return new_text

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

    def determine_wpm_category(self, wpm):
        if wpm >= 150 and wpm <= 160:
            return 5
        if wpm >= 140 and wpm <= 149:
            return 4
        elif wpm >= 130 and wpm <= 139:
            return 3
        elif wpm >= 120 and wpm <= 129:
            return 2
        elif wpm >= 110 and wpm <= 119:
            return 1
        else: 
            return 1


    def perform_all_evaluation(self, given_script: str, transcription: str, audio_path: str):
        y, sr = librosa.load(audio_path)
        energy = self.calculate_energy(y)
        avg_pause_duration = self.calculate_pause_duration(y, sr)
        audio_duration = librosa.get_duration(y=y, sr=sr)
        processed_transcription = self.normalize_transcription(transcription)
        given_script = self.normalize_given_transcription(given_script)
        words_per_minute = self.calculate_words_per_minute(processed_transcription, audio_duration)
        similarity_score = self.calculate_distance_levenshtein(given_script=given_script, transcription=transcription)
        prompt = self.generate_prompt(speaker_transcript=transcription, given_transcript=given_script)
        result = self.evaluate(prompt)
        captured_json_result = self.capture_json_result(result)
        evaluation = self.capture_text_from_result(result)
        metadata = FeatureExtractor(y, sr).extract_audio_quality_as_json()
        wpm_category = self.determine_wpm_category(wpm=words_per_minute)

        scores = {
            "result": result,
            "energy": str(energy),
            "avg_pause_duration": str(avg_pause_duration),
            "audio_duration": audio_duration,
            "words_per_minute": words_per_minute,
            "transcription": processed_transcription,
            "given_transcription": given_script,
            "similarity_score": similarity_score,
            "score_object": captured_json_result,
            "evaluation": evaluation.strip(),
            "audio_path": audio_path,
            "metadata": metadata,
            "wpm_category": wpm_category
        }

        return scores
    
    # Energy Calculation (RMS)
    def calculate_energy(self, y):
        energy = np.sqrt(np.mean(y ** 2))
        return energy
    
    def calculate_pause_duration(self, y, sr, threshold=0.01):
        non_silent_intervals = librosa.effects.split(y, top_db=20)
        pauses = np.diff(non_silent_intervals[:, 0]) / sr
        avg_pause_duration = np.mean(pauses[pauses > threshold]) if len(pauses) > 0 else 0
        return avg_pause_duration

    def calculate_pause_duration_in_seconds(y, sr, threshold=0.01):
        non_silent_intervals = librosa.effects.split(y, top_db=20)
        pauses = np.diff(non_silent_intervals[:, 0]) / sr
        avg_pause_duration = np.mean(pauses[pauses > threshold]) if len(pauses) > 0 else 0
        # Convert average pause duration to seconds
        avg_pause_seconds = avg_pause_duration * sr
        return avg_pause_seconds
    
    def preprocess(self, text: str):
        # Remove punctuation and special characters
        pattern = r'[^a-zA-Z0-9\s]'

        text = re.sub(pattern, '', text)
        # Convert to lowercase
        return text.lower()
    
    def calculate_similarity_score(self, given_script: str, transcription: str):
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer().fit_transform([given_script, transcription])
        vectors = vectorizer.toarray()

        # Calculate cosine similarity
        cosine_sim = cosine_similarity(vectors)
        similarity_score = cosine_sim[0][1]

        return similarity_score
    
    def map_value(self, value, lowest_value, max_value):
        return (value * max_value) + lowest_value
    
    def calculate_distance_levenshtein(self, transcription: str, given_script: str):
        transcription = self.preprocess(transcription)
        given_script = self.preprocess(given_script)

        # Calculate Levenshtein distance
        levenshtein_distance = Levenshtein.distance(transcription, given_script)
        
        # Normalize Levenshtein distance
        max_len = max(len(transcription), len(given_script))
        normalized_distance = levenshtein_distance / max_len
        
        # Similarity score: 1 - normalized Levenshtein distance
        levenshtein_similarity = 1 - normalized_distance
        
        score = math.ceil(self.map_value(levenshtein_similarity, 1, 5))

        if score >= 5:
            return 5

        return score