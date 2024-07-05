import asyncio
import os
from dataclasses import dataclass
import requests
import speech_recognition as sr
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

@dataclass
class Transcriber:
    base_url: str = 'http://172.20.0.6:5432'
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.deepgram = DeepgramClient(api_key=os.getenv('DEEPGRAM_TOKEN'))

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
    
    def transcribe_with_deepgram(self, audio_path: str):
        try:
            with open(audio_path, "rb") as file:
                buffer_data = file.read()

            payload: FileSource = {
                "buffer": buffer_data,
            }

            #STEP 2: Configure Deepgram options for audio analysis
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=False,
                punctuate=False
            )

            # STEP 3: Call the transcribe_file method with the text payload and options
            response = self.deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
            

            # STEP 4: Print the response
            return response['results']['channels'][0]['alternatives'][0]['transcript']

        except Exception as e:
            print(f"Exception: {e}")
        
    async def transcribe_with_deepgram_async(self, audio_path: str):
        try:

            with open(audio_path, "rb") as file:
                buffer_data = file.read()

            payload: FileSource = {
                "buffer": buffer_data,
            }

            #STEP 2: Configure Deepgram options for audio analysis
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=False,
                punctuate=False
            )

            response = await self.deepgram.listen.asyncprerecorded.v("1").transcribe_file(payload, options)

            # STEP 4: Print the response
            return response['results']['channels'][0]['alternatives'][0]['transcript']

        except Exception as e:
            raise Exception("Transcription failed: ", e)