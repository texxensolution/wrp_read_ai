from dataclasses import dataclass
from aiohttp import ClientSession

@dataclass
class Ollama:
    model: str
    host: str = 'http://172.16.1.4:11434/api/chat'
    messages = []

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
                print("llm evaluation...")
                async with session.post(self.host, json=data) as response:
                    response = await response.json()
                    return response['message']['content']
        except Exception as err:
            raise Exception("error:", err) from err
    