from abc import ABC, abstractmethod
from typing import Literal


class ITranscriber(ABC):
    @abstractmethod
    async def transcribe(
        self,
        audio_path: str,
        model: str,
        language: Literal['en', 'tl'] = 'tl'
    ):
        pass
