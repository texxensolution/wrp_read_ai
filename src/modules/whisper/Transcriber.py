from dataclasses import dataclass
import requests
import os

@dataclass
class Transcriber:
    base_url: str = 'http://172.20.0.6:5432'

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
    






