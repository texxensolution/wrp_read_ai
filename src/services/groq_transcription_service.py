import logging
from src.interfaces import ITranscriber
from groq import AsyncGroq
from src.services.api_manager import APIManager
from typing import Literal


logger = logging.getLogger("groq_service")


class GroqTranscriptionService(ITranscriber):
    def __init__(
        self,
        api_manager: APIManager
    ):
        self.client = AsyncGroq(max_retries=3)
        self.api_manager: APIManager = api_manager

    async def transcribe(
        self,
        audio_path: str,
        model: Literal[
            'whisper-large-v3',
            'distil-whisper-large-v3-en'
        ] = 'whisper-large-v3',
        language: Literal['en', 'tl'] = 'tl'
    ):
        api_key = self.api_manager.get_next_key()
        self.client.api_key = api_key
        logger.info("api_key_used: %s", self.client.api_key)

        file = open(audio_path, 'rb')

        transcription = await self.client.audio.transcriptions.create(
            file=(audio_path, file.read()),
            model=model,
            language=language
        )
        return transcription.text
