from pydantic import BaseModel

class ESRecordingRelatedFieldsScore(BaseModel):
    similarity_score: float
    words_per_minute: float