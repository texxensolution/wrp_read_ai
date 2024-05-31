from dotenv import load_dotenv
from jose import jwt
from os import getenv
import time
from dataclasses import dataclass

load_dotenv('.env')

@dataclass
class JWTGenerator:
    secret_key = getenv('SECRET_KEY')

    def generate(self):
        return jwt.encode({
            "sub": "api-key",
            "timestamp": time.time() 
        }, self.secret_key)
    
    def decode(self, token: str):
        return jwt.decode(token, self.secret_key)