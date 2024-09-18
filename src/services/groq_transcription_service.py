from src.interfaces import ITranscriber
from groq import AsyncGroq
from typing import Literal


class GroqTranscriptionService(ITranscriber):
    def __init__(self, token: str):
        self.client = AsyncGroq(api_key=token, max_retries=3)

    async def transcribe(
        self,
        audio_path: str,
        model: Literal[
            'whisper-large-v3',
            'distil-whisper-large-v3-en'
        ] = 'whisper-large-v3',
        language: Literal['en', 'tl'] = 'tl'
    ):
        file = open(audio_path, 'rb')

        transcription = await self.client.audio.transcriptions.create(
            file=(audio_path, file.read()),
            model=model,
            language=language
        )
        return transcription.text
