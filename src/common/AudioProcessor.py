import librosa
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence
from scipy.signal import find_peaks
from typing import Literal

class AudioProcessor:
    
    """audio processor class"""
    @staticmethod
    # Load the audio file
    def remove_silence_from_audio(audio_path, silence_thresh=-50, min_silence_len=500, keep_silence=500, _format: Literal["mp3", "wav"] = "mp3"):
        audio = AudioSegment.from_file(audio_path)

        chunks = split_on_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh, 
            keep_silence=keep_silence 
        )

        processed_audio = AudioSegment.empty()
        for chunk in chunks:
            processed_audio += chunk

        processed_audio.export(audio_path, format=_format)
        return processed_audio.duration_seconds

    @staticmethod
    def determine_wpm_category(wpm):
        """determine the wpm category of the speaker"""
        wpm = int(wpm)
        if wpm > 160 and wpm <= 200:
            return 4
        elif wpm > 120 and wpm <= 160:
            return 5
        elif wpm > 80 and wpm <= 120:
            return 3
        elif wpm >= 0 and wpm < 80:
            return 2
        else:
            return 1

    @staticmethod
    def is_audio_more_than_30_secs(y, sr):
        """check if the audio input is more than 30 secs"""
        duration = librosa.get_duration(y=y, sr=sr)
        return True if duration > 30 else False
    
    @staticmethod
    def determine_pitch_consistency(pitch_std):
        """calculate the std deviation between the pitch of the audio recording"""
        if pitch_std <= 5:
            return 5  # Excellent pitch control
        elif pitch_std <= 10:
            return 4  # Very good pitch control
        elif pitch_std <= 20:
            return 3  # Good pitch control
        elif pitch_std <= 30:
            return 2  # Fair pitch control
        else:
            return 1  # Poor pitch control
    
    @staticmethod
    def pitch_stability_score(y, sr):
        """calculate the pitch stability or the standard deviation of the audio"""
        # Extract pitch (fundamental frequency) using librosa
        pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        # Convert to numpy array for easier manipulation
        pitch_values = np.array(pitch_values)
        
        # Calculate pitch stability (peaks)
        peaks, _ = find_peaks(pitch_values)
        pitch_stability = len(peaks) / len(pitch_values)
        
        # Calculate pitch stability score
        stability_score = AudioProcessor.calculate_stability_score(pitch_stability)
        return stability_score
    
    @staticmethod
    def calculate_stability_score(stability_ratio):
        """Calculate a score from 1 to 5 based on pitch stability ratio."""
        if stability_ratio < 0.1:
            return 1
        elif stability_ratio < 0.222:
            return 2
        elif stability_ratio < 0.223:
            return 3
        elif stability_ratio < 0.224:
            return 4
        else:
            return 5

    @staticmethod
    def calculate_words_per_minute(transcription: str, duration_sec):
        """calculate words per minute using transcription and duration of the audio"""
        return len(transcription.split(' ')) / (duration_sec / 60) # convert duration to minute
    
    @staticmethod
    def determine_speaker_pacing(wpm: float, avg_pause_duration: float):
        """calculate the speaker pacing using word per minute and average pause duration"""
        wpm_score = AudioProcessor.determine_wpm_category(wpm)
        pause_score = AudioProcessor.determine_pause_score(avg_pause_duration)
        final_score = (wpm_score + pause_score) / 2
        return round(final_score) + 1

    @staticmethod
    def determine_pause_score(avg_pause_duration):
        """calculate the pause score of the speaker"""
        if avg_pause_duration <= 0.2:
            return 5
        elif 0.2 < avg_pause_duration <= 0.4:
            return 4
        elif 0.4 < avg_pause_duration <= 0.6:
            return 3
        elif 0.6 < avg_pause_duration <= 0.8:
            return 2
        else:
            return 1