from aiohttp import ClientSession
import json

class BubbleHTTPClientService:
    def __init__(self, bearer_token: str) -> None:
        self.bearer_token = bearer_token 
        
    async def update_reading_score(self, record_id: str, score: int):
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "record_id": record_id,
            "scores": score
        }

        try:
            async with ClientSession() as session:
                async with session.post("https://jobapplication.madridph.com/api/1.1/wf/update_script", headers=headers, data=data) as response:
                    response = await response.json()
                    return response
        except Exception as err:
            raise Exception(f"error: {err}")

        
    async def update_quote_score(self, record_id: str, score: int):
        headers={
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "record_id": record_id,
            "scores": score
        }

        try:
            async with ClientSession() as session:
                async with session.post("https://jobapplication.madridph.com/api/1.1/wf/update_quote", headers=headers, data=data) as response:
                    response = await response.json()
                    return response
        except Exception as err:
            raise Exception(f"error: {err}")
    



        