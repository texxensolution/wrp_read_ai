import Levenshtein
from .utilities import map_value
from .text_preprocessor import TextPreprocessor
import math

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jiwer

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
    

    @staticmethod
    def cosine_text_similarity(text1: str, text2: str) -> float:
        """Calculate the cosine similarity between two texts and return a 1-5 score.
        
        Args:
            text1 (str): The transcribed text from the audio recording
            text2 (str): The original text that was meant to be read/spoken
            
        Returns:
            float: Similarity score from 1-5, where 5 indicates highest similarity
        """
        # Pre-process texts to normalize them
        text1 = TextPreprocessor.normalize(text1)
        text2 = TextPreprocessor.normalize(text2)
        
        # Create and fit vectorizer once for both texts
        vectorizer = TfidfVectorizer(lowercase=True)
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        
        # Calculate cosine similarity directly from matrix
        return 1 + (tfidf_matrix[0].dot(tfidf_matrix[1].T).toarray()[0][0] * 4)

    @staticmethod
    def word_error_rate_score(reference: str, hypothesis: str):
        """Calculate the Word Error Rate (WER) between the original text (reference) and the transcribed text (hypothesis) and return a 1–5 score.
           
           Args:
               reference (str): The original text that was meant to be read/spoken
               hypothesis (str): The actual transcribed text from the audio recording
           
           The jiwer.wer() function calculates the Word Error Rate by:
           1. Normalizing both texts (removing punctuation, converting to lowercase)
           2. Tokenizing into words
           3. Computing minimum number of word-level operations (insertions, deletions, substitutions) 
              needed to transform reference into hypothesis
           4. Dividing total operations by number of words in reference
           
           For example:
           reference: "the cat sat on the mat"
           hypothesis: "a cat sits on mat" 
           Operations: 1 substitution ("sits" for "sat"), 2 deletions ("the", "the")
           WER = 3 operations / 6 reference words = 0.5 or 50% error rate
           
           A lower WER means a higher score, indicating better match between reference and hypothesis."""
        print("Calculating Word Error Rate (WER)...")
        wer_value = jiwer.wer(reference, hypothesis)
        # Cap the WER at 1 (100%) if it exceeds that value.
        wer_value = min(wer_value, 1)
        # Map: 0% error (wer_value = 0) gives a score of 5, 100% error (wer_value = 1) gives a score of 1.
        rating = 5 - (wer_value * 4)
        # Calculate equivalent percentage (rating 1 = 0%, rating 5 = 100%)
        # percentage = ((rating - 1) / 4) * 100
        return rating