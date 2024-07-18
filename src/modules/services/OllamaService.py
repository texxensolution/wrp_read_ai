from aiohttp import ClientSession
from src.modules.interfaces import ILLM

class OllamaService(ILLM):
    def __init__(self, host: str = 'http://172.16.1.4:11434/api/chat', model="llama3:instruct"):
        self.host = host
        self.model = model
    
    async def chat(self, prompt: str):
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
                    return response['message']['content']
        except Exception as err:
            raise Exception("error:", err) from err