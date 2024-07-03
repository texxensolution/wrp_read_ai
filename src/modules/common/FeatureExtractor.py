import librosa
import numpy as np
from dataclasses import dataclass

@dataclass
class FeatureExtractor:
    def __init__(self, y, sr):
        self.y, self.sr = y, sr

    @staticmethod
    def load_audio(y, sr):
        return FeatureExtractor(y, sr)

    def pitches(self, fmin=50, fmax=300):
        # Extract pitch using the librosa.pyin() function
        pitches, voiced_flags, voiced_probs = librosa.pyin(self.y, fmin=50, fmax=300)
        
        # Filter out unvoiced frames
        pitches = pitches[voiced_flags]
        
        # Return the pitch values (in Hz)
        return pitches
    
    def pitch_consistency(self):
        # Extract pitch using the librosa.pyin() function
        pitches = self.pitches()
        return np.std(pitches)

    def calculate_pause_duration(self):
        threshold = 0.2
        non_silent_intervals = librosa.effects.split(y=self.y, top_db=20)
        pauses = np.diff(non_silent_intervals[:, 0]) / self.sr
        avg_pause_duration = np.mean(pauses[pauses > threshold]) if len(pauses) > 0 else 0
        return avg_pause_duration
        
    def serialize_dict_with_array(self, data):
        def convert_value(value):
            if isinstance(value, np.ndarray):
                return value.tolist()
            elif isinstance(value, np.float32) or isinstance(value, np.float64):
                return float(value)
            elif isinstance(value, (np.int32, np.int64)):
                return int(value)
            elif isinstance(value, list):
                return [convert_value(v) for v in value]
            else:
                return value

        serialized_data = {key: convert_value(value) for key, value in data.items()}
        return serialized_data