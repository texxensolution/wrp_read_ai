from pydantic import BaseModel, field_validator


class RequiredFieldsScriptReading(BaseModel):
    user_id: str
    name: str
    email: str
    record_id: str
    audio_url: str
    script_id: str
    no_of_retries: int

    @field_validator('no_of_retries', mode="before")
    def format_no_of_retries(cls, v):
        if isinstance(v, str):
            return int(v)
        return v
