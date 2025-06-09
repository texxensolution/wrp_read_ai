import librosa
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence
from scipy.signal import find_peaks
from typing import Literal
import os

class AudioProcessor:
    """audio processor class"""
    @staticmethod
    # Load the audio file
    def remove_silence_from_audio(
        audio_path,
        silence_thresh=-50,
        min_silence_len=500,
        keep_silence=500,
        _format: Literal["mp3", "wav"] = "mp3"
    ):
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
        stability_score = AudioProcessor.calculate_stability_score(
            pitch_stability
        )
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
        
    @staticmethod
    def cut_and_merge_say_phrases(
        input_path: str,
        cycles: int = 10
    ) -> str:
        """
        Cuts out only the 'say‑phrase' (15 s) from each cycle of:
        15 s show + 5 s ready + 15 s say
        for up to `cycles` repeats, merges them in order,
        overwrites the original file, and prints the timestamps.
        Returns the path to the merged file (same as input_path).
        Supports both .wav and .mp3 files.
        """
        try:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"File not found: {input_path}")
            ext = os.path.splitext(input_path)[1].lower()
            if ext not in [".wav", ".mp3"]:
                raise ValueError("Only .wav and .mp3 files are supported.")

            # --- Load the full audio ---
            audio = AudioSegment.from_file(input_path)
            total_ms = len(audio)

            # --- Define durations ---
            show_ms  = 15 * 1000   # 15 s showing phrase
            ready_ms =  5 * 1000   # 5 s get ready
            say_ms   = 15 * 1000   # 15 s saying phrase
            cycle_ms = show_ms + ready_ms + say_ms

            merged = AudioSegment.empty()
            timestamps = []  # will hold (start_sec, end_sec) tuples

            for i in range(cycles):
                say_start_ms = i * cycle_ms + show_ms + ready_ms
                if say_start_ms >= total_ms:
                    print(f"⏭️ Cycle {i+1} SAY start beyond audio length, stopping.")
                    break

                say_end_ms = min(say_start_ms + say_ms, total_ms)
                merged += audio[say_start_ms:say_end_ms]

                start_sec = say_start_ms / 1000
                end_sec   = say_end_ms   / 1000
                timestamps.append((start_sec, end_sec))
                print(f"  ➕ Appended cycle {i+1} SAY: {start_sec:.1f}s–{end_sec:.1f}s")

            # --- Overwrite the original file ---
            # Export in the same format as input
            export_format = ext[1:]  # remove the dot
            merged.export(input_path, format=export_format)
            print(f"✅ Overwritten merged audio: {input_path}")
            print("Merged SAY‑phrase timestamps (sec):", timestamps)
            return input_path

        except FileNotFoundError as e:
            print(f"❌ File error: {e}")
        except ValueError as e:
            print(f"❌ Value error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")