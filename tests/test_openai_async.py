from openai import AsyncOpenAI
import asyncio
import os

async def evaluate(openai: AsyncOpenAI):
    prompt=[
                {
                    'role': 'system',
                    'content': 'generate unique phrases'
                }
            ]
    
    response = await openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt
    )

    content = response.choices[0].message.content

    return content 

if __name__ == '__main__':
    client = AsyncOpenAI(api_key=os.getenv('OPENAI2_KEY'))
    asyncio.run(evaluate(client))
    
    