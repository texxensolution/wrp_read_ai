import numpy as np
import joblib
import librosa
from dataclasses import dataclass, field
from sklearn.svm import SVC

@dataclass
class AudioClassifier:
    classifier_model_path: str
    classifier: SVC = field(init=False)

    def __post_init__(self):
        self.classifier = joblib.load(self.classifier_model_path)

    def extract_features(self, y, sr):
        try:
            # Extracting various features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfccs_mean = np.mean(mfccs.T, axis=0)
            
            zcr = librosa.feature.zero_crossing_rate(y=y)
            zcr_mean = np.mean(zcr.T, axis=0)
            
            chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_stft_mean = np.mean(chroma_stft.T, axis=0)
            
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            spectral_contrast_mean = np.mean(spectral_contrast.T, axis=0)

            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            centroid_mean = np.mean(centroid)

            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            rolloff_mean = np.mean(rolloff)
            
            rms = librosa.feature.rms(y=y)
            loudness = np.mean(rms.T, axis=0)
            
            mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
            mel_spectrogram_mean = np.mean(mel_spectrogram.T, axis=0)
            
            tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
            tonnetz_mean = np.mean(tonnetz.T, axis=0)

            # Concatenating all features into a single feature vector
            features = np.hstack((
                mfccs_mean, 
                zcr_mean, 
                chroma_stft_mean, 
                spectral_contrast_mean, 
                centroid_mean, 
                rolloff_mean, 
                loudness, 
                mel_spectrogram_mean, 
                tonnetz_mean,
            ))

            return features
        except Exception as e:
            return None

    def predict(self, y, sr):
        features = [self.extract_features(y, sr)]
        return self.classifier.predict(features)

    def predict_prob(self, y, sr):
        features = [self.extract_features(y, sr)]
        return self.classifier.predict_proba(features)
