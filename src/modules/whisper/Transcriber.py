from dataclasses import dataclass
import requests
import speech_recognition as sr

@dataclass
class Transcriber:
    base_url: str = 'http://172.20.0.6:5432'
    
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe_with_timestamp(self, audio_path):
        # create the payload with audio binary
        files = {
            'file': open(audio_path, 'rb')
        }

        try:
            response = requests.post(url=f'{self.base_url}/transcribe_with_timestamp', files=files)

            response = response.json()

            transcription = response['transcription']

            return transcription
        except Exception as e:
            print("Error processing transcription data:", e)  # For debugging
            return "Error processing transcription data"
    
    def transcribe_with_google(self, audio_path: str):
        audio_data = sr.AudioFile(audio_path)
        with audio_data as source:
            audio_content = self.recognizer.record(source)
        try:
            transcription = self.recognizer.recognize_google(audio_content, language="en-US")
        except sr.UnknownValueError as err:
            raise sr.TranscriptionFailed(f"Transcription error: {err}")
        except sr.RequestError as err:
            raise sr.RequestError(f"Request error: {err}")
        return transcription