import json
from dataclasses import dataclass
import requests

@dataclass
class Ollama:
    model: str
    host: str
    messages = []

    def combine_prompt_and_message(self, prompt: str, message: str):
        # self.messages.append({
        #     "role": "assistant",
        #     "content": prompt
        # })
        # self.messages.append({
        #     "role": "user",
        #     "content": message
        # })
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

    def generate(self, prompt: str):
        data = {
            "model": self.model,
            "messages": prompt,
            "stream": False,
            "options": {
                "temperature": 0
            }
        }

        response = requests.post(f"http://{self.host}/api/chat", json=data)

        generated = response.json()

        return generated['message']['content']
    
    def clear_history(self):
        self.messages = []

