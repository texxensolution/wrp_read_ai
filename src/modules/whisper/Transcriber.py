from dataclasses import dataclass
import aiohttp
import asyncio
import requests
import os
import speech_recognition as sr
from pydub import AudioSegment
from src.modules.common import AudioConverter

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
    
    def transcribe_with_google(self, audio_path):
        audio_data = sr.AudioFile(audio_path)

        with audio_data as source:
            audio_content = self.recognizer.record(source)
        try:
            transcription = self.recognizer.recognize_google(audio_content)
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"
        return transcription