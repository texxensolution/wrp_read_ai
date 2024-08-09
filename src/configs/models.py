import json
from .config import Base
from typing import Any
from sqlalchemy import Column, String, Text, Integer

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    payload = Column(Text)

    def __init__(self, type: str, payload: Any):
        self.type = type
        self.payload = json.dumps(payload)
