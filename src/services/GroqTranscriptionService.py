from src.interfaces import ITranscriber
from groq import AsyncGroq
import os

class GroqTranscriptionService(ITranscriber):
    def __init__(self, token: str):
        self.client = AsyncGroq(api_key=token, max_retries=3)
    
    async def transcribe(self, audio_path: str):
        file = open(audio_path, 'rb')

        transcription = await self.client.audio.transcriptions.create(
            file=(audio_path, file.read()),
            model="whisper-large-v3",
        )

        return transcription.text
    


