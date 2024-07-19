from enum import Enum

class BubbleRecordStatus(Enum):
    DONE = "done"
    FAILED = "failed"
    FILE_DELETED = "file deleted"
    INVALID_AUDIO_URL = "INVALID_AUDIO_URL"
    AUDIO_LESS_THAN_30_SECS = "audio_less_than_30_secs"

    def __str__(self) -> str:
        return str(self.value)
