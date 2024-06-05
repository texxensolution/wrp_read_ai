import librosa
import os
import json
import numpy as np
from pydub import AudioSegment
from dataclasses import dataclass

@dataclass
class FeatureExtractor:
    def __init__(self, y, sr):
        self.y, self.sr = y, sr

    def extract_audio_features(self):
        # Extract features
        pitch_mean = librosa.pitch.mean_frequency(y=self.y, sr=self.sr)
        pitch_std = librosa.pitch.tuning(y=self.y, sr=self.sr)[1]
        pitch_modulation = ...  # Compute pitch modulation feature
        loudness = librosa.feature.rms(y=self.y)[0].mean()
        intensity_std = np.std(librosa.feature.rmse(y=self.y))
        spectral_centroid = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0].mean()
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr)[0].mean()
        mfccs = librosa.feature.mfcc(y=self.y, sr=self.sr, n_mfcc=13)
        mfcc_mean = np.mean(mfccs, axis=1)

        # Combine features into a single array
        features = np.hstack([
            pitch_mean, 
            pitch_std, 
            pitch_modulation, 
            loudness, 
            intensity_std,
            spectral_centroid, 
            spectral_bandwidth, 
            mfcc_mean
        ])

        return features
    
    def extract_audio_features_as_json(self):
        pitch_mean = librosa.pitch.mean_frequency(y=self.y, sr=sr)
        pitch_std = librosa.pitch.tuning(y=self.y, sr=sr)[1]
        loudness = librosa.feature.rms(y=self.y)[0].mean()
        intensity_std = np.std(librosa.feature.rmse(y=self.y))
        spectral_centroid = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0].mean()
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr)[0].mean()
        mfccs = librosa.feature.mfcc(y=self.y, sr=self.sr, n_mfcc=13)
        mfcc_mean = np.mean(mfccs, axis=1)

        # Combine features into a single array
        features = {
            "pitch_mean": pitch_mean, 
            "pitch_std": pitch_std, 
            "loudness": loudness, 
            "intensity_std": intensity_std,
            "spectral_centroid": spectral_centroid, 
            "spectral_bandwidth": spectral_bandwidth, 
            "mfcc_mean": mfcc_mean
        }

        return json.dumps(features)

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
            

    def extract_audio_quality_as_json(self):
        # RMS Energy
        rms = librosa.feature.rms(y=self.y).T
        rms_mean = np.mean(rms, axis=0)
        rms_std = np.std(rms, axis=0)
        rms_min = np.min(rms, axis=0)
        rms_max = np.max(rms, axis=0)

        # Spectral Centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=self.y, sr=self.sr).T
        spectral_centroid_mean = np.mean(spectral_centroid, axis=0)
        spectral_centroid_std = np.std(spectral_centroid, axis=0)
        spectral_centroid_min = np.min(spectral_centroid, axis=0)
        spectral_centroid_max = np.max(spectral_centroid, axis=0)

        # Zero Crossing Rate
        zero_crossing_rate = librosa.feature.zero_crossing_rate(self.y).T
        zero_crossing_rate_mean = np.mean(zero_crossing_rate, axis=0)
        zero_crossing_rate_std = np.std(zero_crossing_rate, axis=0)
        zero_crossing_rate_min = np.min(zero_crossing_rate, axis=0)
        zero_crossing_rate_max = np.max(zero_crossing_rate, axis=0)

        # Pitch
        pitches, magnitudes = librosa.core.piptrack(y=self.y, sr=self.sr)
        pitch_values = pitches[pitches > 0]
        pitch_mean = np.mean(pitch_values) if len(pitch_values) > 0 else 0
        pitch_std = np.std(pitch_values) if len(pitch_values) > 0 else 0
        pitch_min = np.min(pitch_values) if len(pitch_values) > 0 else 0
        pitch_max = np.max(pitch_values) if len(pitch_values) > 0 else 0

        # MFCCs
        mfccs = librosa.feature.mfcc(y=self.y, sr=self.sr)
        mfcc_mean = np.mean(mfccs.T, axis=0)
        mfcc_std = np.std(mfccs.T, axis=0)
        mfcc_min = np.min(mfccs.T, axis=0)
        mfcc_max = np.max(mfccs.T, axis=0)

        # Chroma Features
        chroma = librosa.feature.chroma_stft(y=self.y, sr=self.sr)
        chroma_mean = np.mean(chroma.T, axis=0)
        chroma_std = np.std(chroma.T, axis=0)
        chroma_min = np.min(chroma.T, axis=0)
        chroma_max = np.max(chroma.T, axis=0)

        # Spectral Bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr).T
        spectral_bandwidth_mean = np.mean(spectral_bandwidth, axis=0)
        spectral_bandwidth_std = np.std(spectral_bandwidth, axis=0)
        spectral_bandwidth_min = np.min(spectral_bandwidth, axis=0)
        spectral_bandwidth_max = np.max(spectral_bandwidth, axis=0)

        # Spectral Contrast
        spectral_contrast = librosa.feature.spectral_contrast(y=self.y, sr=self.sr).T
        spectral_contrast_mean = np.mean(spectral_contrast, axis=0)
        spectral_contrast_std = np.std(spectral_contrast, axis=0)
        spectral_contrast_min = np.min(spectral_contrast, axis=0)
        spectral_contrast_max = np.max(spectral_contrast, axis=0)

        # Harmonic-to-Noise Ratio
        harmonic_ratio = librosa.effects.harmonic(y=self.y)
        hnr_mean = np.mean(harmonic_ratio)
        hnr_std = np.std(harmonic_ratio)
        hnr_min = np.min(harmonic_ratio)
        hnr_max = np.max(harmonic_ratio)

        # Tempo
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.sr)

        # Spectral Roll-off
        spectral_rolloff = librosa.feature.spectral_rolloff(y=self.y, sr=self.sr).T
        spectral_rolloff_mean = np.mean(spectral_rolloff, axis=0)
        spectral_rolloff_std = np.std(spectral_rolloff, axis=0)
        spectral_rolloff_min = np.min(spectral_rolloff, axis=0)
        spectral_rolloff_max = np.max(spectral_rolloff, axis=0)

        # Spectral Flatness
        spectral_flatness = librosa.feature.spectral_flatness(y=self.y).T
        spectral_flatness_mean = np.mean(spectral_flatness, axis=0)
        spectral_flatness_std = np.std(spectral_flatness, axis=0)
        spectral_flatness_min = np.min(spectral_flatness, axis=0)
        spectral_flatness_max = np.max(spectral_flatness, axis=0)

        # Speech Rate (Words per Minute)
        duration_in_minutes = librosa.get_duration(y=self.y, sr=self.sr) / 60

        # Pause Patterns
        pauses = np.where(np.abs(self.y) < 0.001)[0]
        pause_durations = np.diff(pauses)
        pause_mean = np.mean(pause_durations) if len(pause_durations) > 0 else 0
        pause_std = np.std(pause_durations) if len(pause_durations) > 0 else 0
        pause_min = np.min(pause_durations) if len(pause_durations) > 0 else 0
        pause_max = np.max(pause_durations) if len(pause_durations) > 0 else 0
        pause_frequency = len(pause_durations) / duration_in_minutes if duration_in_minutes > 0 else 0

        data = {
            "rms_mean": rms_mean,
            "rms_std": rms_std,
            "rms_min": rms_min,
            "rms_max": rms_max,
            "spectral_centroid_mean": spectral_centroid_mean.tolist(),
            "spectral_centroid_std": spectral_centroid_std.tolist(),
            "spectral_centroid_min": spectral_centroid_min.tolist(),
            "spectral_centroid_max": spectral_centroid_max.tolist(),
            "zero_crossing_rate_mean": zero_crossing_rate_mean.tolist(),
            "zero_crossing_rate_std": zero_crossing_rate_std.tolist(),
            "zero_crossing_rate_min": zero_crossing_rate_min.tolist(),
            "zero_crossing_rate_max": zero_crossing_rate_max.tolist(),
            "pitch_mean": pitch_mean,
            "pitch_std": pitch_std,
            "pitch_min": pitch_min,
            "pitch_max": pitch_max,
            "mfcc_mean": mfcc_mean.tolist(),
            "mfcc_std": mfcc_std.tolist(),
            "mfcc_min": mfcc_min.tolist(),
            "mfcc_max": mfcc_max.tolist(),
            "chroma_mean": chroma_mean.tolist(),
            "chroma_std": chroma_std.tolist(),
            "chroma_min": chroma_min.tolist(),
            "chroma_max": chroma_max.tolist(),
            "spectral_bandwidth_mean": spectral_bandwidth_mean.tolist(),
            "spectral_bandwidth_std": spectral_bandwidth_std.tolist(),
            "spectral_bandwidth_min": spectral_bandwidth_min.tolist(),
            "spectral_bandwidth_max": spectral_bandwidth_max.tolist(),
            "spectral_contrast_mean": spectral_contrast_mean.tolist(),
            "spectral_contrast_std": spectral_contrast_std.tolist(),
            "spectral_contrast_min": spectral_contrast_min.tolist(),
            "spectral_contrast_max": spectral_contrast_max.tolist(),
            "hnr_mean": hnr_mean,
            "hnr_std": hnr_std,
            "hnr_min": hnr_min,
            "hnr_max": hnr_max,
            "spectral_rolloff_mean": spectral_rolloff_mean.tolist(),
            "spectral_rolloff_std": spectral_rolloff_std.tolist(),
            "spectral_rolloff_min": spectral_rolloff_min.tolist(),
            "spectral_rolloff_max": spectral_rolloff_max.tolist(),
            "spectral_flatness_mean": spectral_flatness_mean.tolist(),
            "spectral_flatness_std": spectral_flatness_std.tolist(),
            "spectral_flatness_min": spectral_flatness_min.tolist(),
            "spectral_flatness_max": spectral_flatness_max.tolist(),
            "pause_mean": pause_mean.tolist(),
            "pause_std": pause_std.tolist(),
            "pause_min": pause_min,
            "pause_max": pause_max,
            "pause_frequency": pause_frequency
        }

        data = self.serialize_dict_with_array(data)

        return json.dumps(data)
