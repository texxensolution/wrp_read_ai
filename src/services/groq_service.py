import os
from src.interfaces import ILLM
from groq import AsyncGroq

class GroqService(ILLM):
    def __init__(self, token=os.getenv('GROQ_API_KEY')):
        self.client = AsyncGroq(
            api_key=token,
        )
    
    async def chat(self, prompt: str):
        try:
            completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    }
                ],
                model="llama3-70b-8192",
                max_tokens=8192,
                temperature=0.5
            )

            return completion.choices[0].message.content
        except Exception as err:
            raise Exception(err) from err

