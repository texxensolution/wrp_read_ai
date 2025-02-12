from pydantic import BaseModel

class RecordingRelatedFieldsScore(BaseModel):
    similarity_score: float
    avg_pause_duration: float
    wpm_category: float
    pronunciation: float
    fluency: float
    voice_classification: float
    pacing_score: float
    words_per_minute: float
