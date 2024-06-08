from src.modules.common import PhonemicAnalysis
import librosa
import speech_recognition as sr

audio_path = "1.wav"

audio_data = sr.AudioFile(audio_path)

recognizer = sr.Recognizer()

with audio_data as source:
    audio_content = recognizer.record(source)
try:
    transcription = recognizer.recognize_google(audio_content)
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")

y, sr = librosa.load(audio_path)

phonemic = PhonemicAnalysis()
df, overall_score, transcription, stress_mismatches  = phonemic.run_analysis(y, sr, transcription, 'script-0001')

print(f"overall score: {overall_score}")
print(f"transcription: {transcription}")