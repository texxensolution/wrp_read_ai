import asyncio
from aiohttp import ClientSession

async def chat_async(prompt: str):
    """async wrapper for ollama chat request"""
    data = {
        "model": "llama3:instruct",
        "messages": [{"role": "system", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0
        }
    }
    try:
        async with ClientSession() as session:
            async with session.post('http://172.16.1.4:11434/api/chat', json=data) as response:
                response = await response.json()
                return response['message']['content'], 0
    except Exception as err:
        raise Exception("error:", err) from err
    
async def main():
    result = await chat_async("hello, world")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())