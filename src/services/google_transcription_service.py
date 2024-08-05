from speech_recognition import Recognizer, AudioFile, TranscriptionFailed, RequestError, UnknownValueError
from src.interfaces import ITranscriber

class GoogleTranscriptionService(ITranscriber):
    """Google transcription service"""
    def __init__(self):
        self.recognizer = Recognizer()
        
    async def transcribe(self, audio_path: str):
        audio_data = AudioFile(audio_path)
        with audio_data as source:
            audio_content = self.recognizer.record(source)
        try:
            transcription = self.recognizer.recognize_google(audio_content, language="en-US")
        except UnknownValueError as err:
            raise TranscriptionFailed(f"Transcription error: {err}")
        except RequestError as err:
            raise RequestError(f"Request error: {err}")
        return transcription