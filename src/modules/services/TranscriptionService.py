from src.modules.interfaces import ITranscriber

class TranscriptionService:
    def __init__(self, client: ITranscriber):
        self.client = client
        
    async def transcribe(self, audio_path: str):
        """function interface for transcribing audio"""
        return await self.client.transcribe(audio_path)
