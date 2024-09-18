from src.interfaces import ITranscriber
from typing import Dict, Literal


class TranscriptionService:
    def __init__(
        self,
        clients: Dict[str, ITranscriber],
        default_client: Literal["groq", "deepgram"] = "deepgram"
    ):
        self.implementations = clients
        self.client = clients[default_client]
        
    async def transcribe(
        self,
        audio_path: str,
        model: str,
        client: Literal["groq", "deepgram", None] = None,
        language: Literal['en', 'tl'] = 'tl'
    ) -> str:
        """function interface for transcribing audio"""
        if client:
            return await self.implementations[client].transcribe(
                audio_path,
                model,
                language=language
            )
        return await self.client.transcribe(audio_path)
