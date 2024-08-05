import Levenshtein
from .utilities import map_value
from .text_preprocessor import TextPreprocessor
import math

class TranscriptionProcessor:
    @staticmethod
    def compute_distance(transcription: str, given_script: str):
        """compute the distance between two string input using levenshtein algorithm"""
        transcription = TextPreprocessor.normalize(transcription)
        given_script = TextPreprocessor.normalize(given_script)

        # Calculate Levenshtein distance
        levenshtein_distance = Levenshtein.distance(transcription, given_script)
        
        # Normalize Levenshtein distance
        max_len = max(len(transcription), len(given_script))
        normalized_distance = levenshtein_distance / max_len
        
        # Similarity score: 1 - normalized Levenshtein distance
        levenshtein_similarity = 1 - normalized_distance

        return levenshtein_similarity * 5