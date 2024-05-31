from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from os import getenv
from jose import jwt, JWTError

load_dotenv('.env')

SECRET_KEY = getenv('SECRET_KEY')

security = HTTPBearer()


def verify_token(token: str = Depends(security)):
    """
        Verify if the header contains Authorization header and check if the token is valid.
        If the token is valid return the content of the message/sub
        If not raise an HTTPException with status code of 401
    """
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=['HS256'])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token or expired token')
