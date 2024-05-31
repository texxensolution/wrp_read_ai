import requests
from dotenv import load_dotenv
from os import getenv, system
from http import HTTPStatus
from pydub import AudioSegment
import json

load_dotenv()

ENDPOINT = 'http://127.0.0.1:8000/api/v1'


def test_authenticated_audio_analyzer():
    api_key = getenv('TEST_API_KEY')

    headers = {'Authorization': f'Bearer {api_key}'}

    given_script = """
    Sa Silong ng Buwan
    (By the Moon's Shelter)

    Sa dilim ng gabi, ako'y lumalakad
    Naglalakbay sa dilim, tadhana'y tinatahak
    Sa silong ng buwan, lihim na bumabalot
    Sa ilalim ng bituin, pangarap ay sumasalot

    Beneath the cloak of night, I wander alone
    Through shadows I tread, destiny's unknown
    Under the moon's shelter, secrets enfold
    Beneath the stars' gaze, dreams take hold

    Bawat hakbang, tibok ng puso'y sumasabay
    Sa himig ng hangin, pag-asa'y sumasalubong
    Sa gabing tahimik, lihim na mundo'y dumaramay
    Sa liwanag ng buwan, damdamin ay naglalambing

    Every step, my heart beats in tune
    With the wind's melody, hope sings soon
    In the quiet night, a secret world to share
    In the moon's light, feelings so rare

    Sa silong ng buwan, tayo'y nagtatagpo
    Mga puso'y naglalapit, nagkakaisa sa puso
    Sa bawat titig, kwento ng pag-ibig
    Sa magdamag na yakap, pag-asa'y dumarami

    Beneath the moon's shelter, we find each other
    Hearts drawing near, united forever
    In every glance, a tale of love's embrace
    In the endless night's embrace, hope finds its place
    """

    files = {
        "file": ('test.wav', open('tests\\audios\\arleah.mp3', 'rb')),
        'applicant_id': (None, '001'),
        'callback_url': (None, 'http://172.20.0.252:8000/ping'),
    }

    response = requests.post(f'{ENDPOINT}/audio/analyze', headers=headers, files=files)

    assert response.status_code == HTTPStatus.OK


def test_unauthenticated_audio_analyzer():
    api_key = 'random'

    headers = {'Authorization': f'Bearer {api_key}'}

    response = requests.post(f'{ENDPOINT}/audio/analyze', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


test_authenticated_audio_analyzer()