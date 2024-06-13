import soundfile as sf
from pydub import AudioSegment
import speech_recognition as sr
import librosa
import numpy as np
import pandas as pd
import difflib
import json
import os

class PhonemicAnalysis:
    def __init__(self, transcription: str, script_id: str):
        self.transcription = transcription
        self.word_stress = []
        self.stress_mismatches = []
        self.phonemic_dataset = []
        self.overall_score = 0
        self.highest_possible_score = 0
        self.dictionary = pd.read_csv('dictionary.csv')
        self.load_script_metadata(script_id)

    def load_script_metadata(self, script_id: str):
        record = self.find_record('script_id', script_id)
        self.expected_stress = record['expected_stressed'].replace("'", '"') # Convert string to dictionary
        self.expected_stress = json.loads(self.expected_stress)
        self.script = record['script']
        self.phonetic_rules = record['phonetic_rules'].replace("'", '"')  # Convert string to dictionary
        self.phonetic_rules = json.loads(self.phonetic_rules)
   

    def find_record(self, column: str, value: str):
        filtered_df = self.dictionary.loc[self.dictionary[column] == value]

        # If you only want to get the first record matching the criteria
        if not filtered_df.empty:
            first_record = filtered_df.iloc[0]
            return first_record
        return None

        
    def extract_prosodic_features(self, y, sr):
        try:
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            intensity = librosa.feature.rms(y=y)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            durations = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
            return pitches, magnitudes, intensity, durations
        except Exception as e:
            raise ValueError(f"Error extracting prosodic features: {e}")

    def identify_stress(self, pitches, magnitudes, intensity, durations):
        stressed_syllables = []
        threshold_pitch = np.mean(pitches) + np.std(pitches)
        threshold_intensity = np.mean(intensity) + np.std(intensity)
        for i in range(len(durations)):
            if pitches[0, durations[i]] > threshold_pitch and intensity[0, durations[i]] > threshold_intensity:
                stressed_syllables.append(durations[i])
        return stressed_syllables

    def map_stress_to_words(self, stressed_syllables):
        words = self.transcription.split()
        self.word_stress = [(word, "stressed" if i in stressed_syllables else "unstressed") for i, word in enumerate(words)]

    def compare_stress(self):
        self.stress_mismatches = []
        for word, stress in self.word_stress:
            expected = self.expected_stress.get(word.lower(), None)
            if expected and stress == 'unstressed' and 'ˈ' in expected:
                self.stress_mismatches.append((word, "expected stressed but detected unstressed"))
            elif expected and stress == 'stressed' and 'ˈ' not in expected:
                self.stress_mismatches.append((word, "expected unstressed but detected stressed"))

    def phonetic_transcription(self, text, rules):
        words = text.split()
        return ' '.join([rules.get(word.lower(), word) for word in words])

    def compare_words(self, script_word, transcription_word):
        d = difflib.Differ()
        diff = list(d.compare([script_word], [transcription_word]))
        score = 5
        for i in diff:
            if i.startswith('- '):  # Missing phoneme
                score -= 1
            elif i.startswith('+ '):  # Extra phoneme
                score -= 1
            elif i.startswith('? '):  # Mispronunciation
                score -= 1
        return max(score, 1)

    def evaluate_phonetic_accuracy(self):
        script_phonetic = self.phonetic_transcription(self.script, self.phonetic_rules)
        transcription_phonetic = self.phonetic_transcription(self.transcription, self.phonetic_rules)
        script_words = script_phonetic.split()
        transcription_words = transcription_phonetic.split()
        self.phonemic_dataset = []
        total_score = 0
        total_stress_penalty = 0

        for transcription_word in transcription_words:
            closest_match = difflib.get_close_matches(transcription_word, script_words, n=1, cutoff=0.0)
            if closest_match:
                script_word = closest_match[0]
                score = self.compare_words(script_word, transcription_word)
                total_score += score
                stress_penalty = self.calculate_stress_penalty(script_word, transcription_word)
                total_stress_penalty += stress_penalty
                self.phonemic_dataset.append({
                    'Script Word': script_word,
                    'Transcription Word': transcription_word,
                    'Pronunciation Accuracy': score,
                    'Stress Penalty': stress_penalty
                })
                script_words.remove(script_word)  # Remove the matched word to avoid duplicate matches
            else:
                self.phonemic_dataset.append({
                    'Script Word': '',
                    'Transcription Word': transcription_word,
                    'Pronunciation Accuracy': 0,
                    'Stress Penalty': 0
                })

        self.overall_score = (total_score - total_stress_penalty) / len(transcription_words) if transcription_words else 0
        self.highest_possible_score = len(transcription_words) * 5 if transcription_words else 0

    def calculate_stress_penalty(self, script_word, transcription_word):
        stress_penalty = 0
        for word, stress in self.word_stress:
            if word == transcription_word:
                expected = self.expected_stress.get(script_word.lower(), None)
                if expected and stress == 'unstressed' and 'ˈ' in expected:
                    stress_penalty += 1
                elif expected and stress == 'stressed' and 'ˈ' not in expected:
                    stress_penalty += 1
        return stress_penalty

    def save_results(self):
        df = pd.DataFrame(self.phonemic_dataset)
        return df

    def run_analysis(self, y, sr):
        try:
            pitches, magnitudes, intensity, durations = self.extract_prosodic_features(y, sr)
            stressed_syllables = self.identify_stress(pitches, magnitudes, intensity, durations)
            self.map_stress_to_words(stressed_syllables)
            self.compare_stress()
            self.evaluate_phonetic_accuracy()
            df = self.save_results()
            return self.overall_score
        except ValueError as e:
            return None, str(e), None, None