from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import Levenshtein
import re
import math

def preprocess(text: str):
        # Remove punctuation and special characters
        pattern = r'[^a-zA-Z0-9\s]'

        text = re.sub(pattern, '', text)
        # Convert to lowercase
        return text.lower().strip()

def map_value(value, lowest_value, max_value):
        return (value * max_value) + lowest_value

def calculate_distance_levenshtein(transcription: str, given_script: str):
    transcription = preprocess(transcription)
    given_script = preprocess(given_script)

    # Calculate Levenshtein distance
    levenshtein_distance = Levenshtein.distance(transcription, given_script)
    
    # Normalize Levenshtein distance
    max_len = max(len(transcription), len(given_script))
    normalized_distance = levenshtein_distance / max_len
    
    # Similarity score: 1 - normalized Levenshtein distance
    levenshtein_similarity = 1 - normalized_distance

    # map the normalized distance from 1-5 scoring
    levenshtein_similarity = map_value(levenshtein_similarity, 1, 5)
    
    # get the ceiling of map_value -> [1, 2, 3, 4, 5]
    return math.ceil(levenshtein_similarity)

def calculate_similarity_score(given_script: str, transcription: str):
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer().fit_transform([given_script, transcription])
        vectors = vectorizer.toarray()

        # Calculate cosine similarity
        cosine_sim = cosine_similarity(vectors)
        similarity_score = cosine_sim[0][1]

        print(f"Similarity score: {similarity_score}")

        return similarity_score

text1 = """
    in a quiet village beside a meandering river a majestic willow tree stood its branches cascading like flowing water villagers called it the whispering willow for it was said to whisper secrets of the past to those who listened closely  one summer evening young thomas wandered into the willows
"""

text2 = """
    in a quiet village beside a meandering river a majestic willow tree stood its branches cascading like flowing water villagers called it the whispering willow for it was said to whisper secrets of the past to those who listened closely  one summer evening young thomas wandered into the willows shade he heard faint whispers carried on the breeze leading him to a hidden nook where an old diary lay among the roots it belonged to eliza a girl from centuries past who told of the willows tragic history  long ago a cruel nobleman planted the willow as a symbol of power causing suffering to the villagers elizas diary spoke of a key hidden within the willows roots that could set its spirit free  determined to help thomas found the key and unlocked a hidden lock on the willows trunk a soft glow emanated and a breeze rustled the branches the willows spirit was free bringing peace to the village  no longer whispering tales of sorrow the willow sang with joy its branches swaying in celebration thomas the boy who listened to its whispers and freed its spirit became a hero his name forever honored in the villages history
"""

text1_a = "test test test test"
text2_b = "test test test"

# print(weighted_similarity_score(text1, text2))
# print(weighted_similarity_score(text1_a, text2_b))
print('combined', math.ceil(map_value(calculate_distance_levenshtein(text1, text2), 1, 5)))

print(calculate_similarity_score(text1_a, text2_b))