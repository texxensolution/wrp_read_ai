import asyncio
import requests
from aiohttp import ClientSession

def chat_async(prompt: str):
    """async wrapper for ollama chat request"""
    data = {
        "model": "llama3:instruct",
        "messages": [{"role": "system", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0
        }
    }
    
    response = requests.post('http://172.16.1.4:11434/api/chat', json=data)

    print(response)
    # try:
    #     async with ClientSession() as session:
    #         async with session.post('http://172.16.1.4:11434/api/chat', json=data) as response:
    #             response = await response.json()
    #             return response['message']['content'], 0
    # except Exception as err:
    #     raise Exception("error:", err) from err
    
if __name__ == "__main__":
    chat_async("hello, world")