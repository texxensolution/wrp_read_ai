from fastapi import FastAPI
from api.audio_analyzer import router as audio_analyzer_router
from os import getenv
from dotenv import load_dotenv

load_dotenv('.env')

SECRET_KEY = getenv('SECRET_KEY')

app = FastAPI()

# include audio analyzer router
app.include_router(audio_analyzer_router, prefix='/api/v1')