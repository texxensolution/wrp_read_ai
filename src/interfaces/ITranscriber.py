from abc import ABC, abstractmethod

class ITranscriber(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: str):
        pass