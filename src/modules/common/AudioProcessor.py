class AudioProcessor:
    @staticmethod
    def determine_wpm_category(wpm):
        if wpm >= 151 and wpm <= 170:
            return 5
        if wpm >= 131 and wpm <= 150:
            return 4
        elif wpm >= 111 and wpm <= 130:
            return 3
        elif wpm >= 90 and wpm <= 110:
            return 2
        else:
            return 1
    
    @staticmethod
    def determine_pitch_consistency(pitch_std):
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
    def calculate_words_per_minute(transcription: str, duration_sec):
        return len(transcription.split(' ')) / (duration_sec / 60) # convert duration to minute
    
    @staticmethod
    def determine_speaker_pacing(wpm: float, avg_pause_duration: float):
        wpm_score = AudioProcessor.determine_wpm_category(wpm)
        pause_score = AudioProcessor.determine_pause_score(avg_pause_duration)
        final_score = (wpm_score + pause_score) / 2
        return round(final_score) + 1

        
    @staticmethod
    def determine_pause_score(avg_pause_duration):
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
        


