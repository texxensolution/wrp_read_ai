import os

import openai
import requests
from tqdm import tqdm
import pandas as pd
import time
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI2_KEY'))


def generate_unique_taglish_scripts():
    retries = 0
    max_retries = 3
    while retries < max_retries:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates random long paragraphs tagalog english references comes from books, poems, call center related communication texts."},
                ],
            )

            print(response.choices)
            return response.choices
        except openai.RateLimitError as err:
            print(f'Error: {err.message}')
            print('retrying in 20secs...')
            retries += 1
            time.sleep(20)


items = []
for epoch in range(10):
    for i in tqdm(range(20)):
        choices = generate_unique_taglish_scripts()

        if choices:
            for choice in choices:
                items.append(choice.message.content)

    df = pd.DataFrame({
        "gpt_result": items
    })

    df.to_csv(f'{time.time()}-result.csv', index=False)

# for epoch in tqdm(range(5)):
#     for i in tqdm(range(20)):
#         generated = generate_unique_taglish_scripts()
#         items.append(generated)
#
#     df = pd.DataFrame({
#         "scripts": items
#     })

    # df.to_csv(f'{time.time()}-scripts.csv', index=False)
