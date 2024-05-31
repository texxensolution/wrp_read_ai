from .Ollama import Ollama
from pydub import AudioSegment
import numpy as np
import librosa
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Eloquent:
    def __init__(self, model = 'llama3:instruct', host = os.getenv('OLLAMA_HOST')):
        self.fillers = ['ay', 'ah', 'eh', 'ano', 'um', 'uhm']
        self.pronunciation_check_prompt = self.add_filler_to_the_prompt("""
            "Please evaluate the participant's spoken language proficiency based on the following criteria and assign a score:
            Criteria:
                1. Pronunciation: Assess the accuracy of word pronunciations according to standard language conventions. Provide a score from 1 (poor) to 5 (excellent).
                2. Enunciation: Evaluate the clarity and precision in articulating individual sounds and words. Assign a score from 1 (unclear) to 5 (crystal clear)."
            - Give brief description about the score
            - format the score as {score: score}
        """, self.fillers)

        self.diction_check_prompt = self.add_filler_to_the_prompt("""
            Please evaluate the participant's spoken language proficiency based on the following criterion and assign a score:

            Criteria: Diction
              Clarity of Expression: Assess how clearly the participant communicates ideas and concepts, avoiding ambiguity or confusion. Provide a score from 1 (unclear) to 5 (crystal clear).
            - Give brief description about the score
            - format the score as {score: score}
        """, self.fillers)

        self.accuracy_check_prompt = self.add_filler_to_the_prompt("""
            Assess the participant's spoken language proficiency based on the following criterion and assign a score:

            Criteria: Accuracy
            Grammar and Syntax: Evaluate the correctness of the participant's grammar and sentence structure. Provide a score from 1 (poor) to 5 (excellent).
            -Give brief description about the score
            - format the score as {score: score}
        """, self.fillers)

        self.aggregate_score_prompt = """
            Aggregate all the scores provided and calculate the overall score of the evaluated results.
            - Calculate the average score for all given {score: number}
            - return only the list of criteria and score
        """

        self.ollama = Ollama(model, host)

    def add_filler_to_the_prompt(self, prompt, fillers=[]):
        joined_fillers = ", ".join(fillers)
        return f"""
            {prompt} \n
            rules:
                demerit the speaker if he uses filler words listed below: \n
                [{joined_fillers}]
        """

    def evaluate_speaker_pauses(self, audio_path):
        audio = AudioSegment.from_file(audio_path)
    
    def evaluate_pronunciation_score(self, answer):
        combined_prompt_answer = self.ollama.combine_prompt_and_message(prompt=self.pronunciation_check_prompt, message=answer)
        return self.evaluate(combined_prompt_answer)

    def evaluate_diction_score(self, answer):
        combined_prompt_answer = self.ollama.combine_prompt_and_message(prompt=self.diction_check_prompt, message=answer)
        return self.evaluate(combined_prompt_answer)

    def evaluate_accuracy_score(self, answer):
        combined_prompt_answer = self.ollama.combine_prompt_and_message(prompt=self.accuracy_check_prompt, message=answer)
        return self.evaluate(combined_prompt_answer)

    def aggregate_scores(self, scores=[]):
        evaluated_scores = "\n\n".join(scores)

        combined_prompt = self.ollama.combine_prompt_and_message(self.aggregate_score_prompt, evaluated_scores)

        return self.ollama.generate(combined_prompt)

    def evaluate(self, combined_prompt_answer):
        return self.ollama.generate(combined_prompt_answer)

    def get_transcription(self, transcription: str):
        transcripts = []
        lines = transcription.split('\n')
        # timestamp, transcript = transcription.split(' : : ')
        for line in lines:
            timestamp, transcript = line.split(' : : ')
            transcript = transcript.strip()
            transcripts.append(transcript)
            return "\n".join(transcripts)

    def calculate_words_per_minute(self, transcription: str, duration):
        return len(transcription.split(' ')) / (duration / 60) # convert duration to minute
        
    def perform_all_evaluation(self, transcription: str, audio_path: str):
        y, sr = librosa.load(audio_path)
        pronunciation_score = self.evaluate_pronunciation_score(transcription)
        diction_score = self.evaluate_diction_score(transcription)
        accuracy_score = self.evaluate_accuracy_score(transcription)
        aggregated_scores = self.aggregate_scores([pronunciation_score, diction_score, accuracy_score])
        energy = self.calculate_energy(y)
        avg_pause_duration = self.calculate_pause_duration(y, sr)
        audio_duration = librosa.get_duration(y=y, sr=sr)
        processed_transcription = self.get_transcription(transcription)
        words_per_minute = self.calculate_words_per_minute(processed_transcription, audio_duration)

        scores = {
            "pronunciation_score": pronunciation_score,
            "diction_score": diction_score,
            "accuracy_score": accuracy_score,
            "aggregated_scores": aggregated_scores,
            "energy": str(energy),
            "avg_pause_duration": str(avg_pause_duration),
            "audio_duration": audio_duration,
            "words_per_minute": words_per_minute,
            "transcription": processed_transcription
        }
        print(scores)
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
    
    # def calculate_similarity_score():
       
    # def preprocess(text):
    #     # Remove punctuation and special characters
    #     text = re.sub(r'[^\w\s]', '', text)
    #     # Convert to lowercase
    #     text = text.lower()
    #     return text

    # # Original script and transcribed text
    # script = "Your original script goes here."
    # transcribed_text = "The transcribed speech goes here."

    # # Preprocess the texts
    # script_processed = preprocess(script)
    # transcribed_processed = preprocess(transcribed_text)

    # # Create TF-IDF vectors
    # vectorizer = TfidfVectorizer().fit_transform([script_processed, transcribed_processed])
    # vectors = vectorizer.toarray()

    # # Calculate cosine similarity
    # cosine_sim = cosine_similarity(vectors)
    # similarity_score = cosine_sim[0][1]

    # print(f"Similarity score: {similarity_score}")

    # # Evaluate the result
    # if similarity_score > 0.8:  # You can set your own threshold
    #     print("The speaker followed the script closely.")
    # else:
    #     print("The speaker did not follow the script closely.")