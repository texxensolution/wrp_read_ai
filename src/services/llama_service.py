from aiohttp import ClientSession
from typing import Literal

from langchain_groq import ChatGroq
from pydantic import BaseModel

from src.interfaces import ILLM

class LlamaService:
    def __init__(self, client: ILLM):
        self.client = client

    async def chat(
        self,
        prompt: str,
    ):
        return await self.client.chat(prompt)