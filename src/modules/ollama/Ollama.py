from dataclasses import dataclass
from aiohttp import ClientSession
from groq import AsyncGroq
import os

class Ollama:
    def __init__(self, model: str, host: str = 'http://172.16.1.4:11434/api/chat'):
        self.model: str = model
        self.host: str = host
        self.groq_client = AsyncGroq(
            api_key=os.getenv('GROQ_API_KEY')
        )

    def combine_prompt_and_message(self, prompt: str, message: str):
        prompt_message = [
            {
                "role": "assistant",
                "content": prompt
            },
            {
                "role": "user",
                "content": message 
            },
        ]
        return prompt_message

    async def chat_async(self, prompt: str):
        """async wrapper for ollama chat request"""
        data = {
            "model": self.model,
            "messages": [{"role": "system", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": 0
            }
        }
        try:
            async with ClientSession() as session:
                async with session.post(self.host, json=data) as response:
                    response = await response.json()
                    return response['message']['content'], 0
        except Exception as err:
            raise Exception("error:", err) from err
    
    async def groq_chat_async(self, prompt: str):
        completion = await self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192"
        )

        return completion.choices[0].message.content, 0