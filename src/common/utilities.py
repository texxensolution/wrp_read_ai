from typing import Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import os
from functools import wraps
from time import sleep

from src.dtos import RequiredFieldsScriptReading


def retry(retries: int = 3, delay: int = 3):
    def decorator_retry(func):
        @wraps(func)
        def wrapper_retry(*args, **kwargs):
            for _ in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    print(f"Retry failed ({_ + 1}/{retries}): {err}")
                    delay *= retries
                    sleep(delay)
            else:
                raise Exception("Max retries exceeded")
        return wrapper_retry
    return decorator_retry

def create_session_with_retries(
    total_retries=3,
    backoff_factor=0.3,
    status_forcelist=[500, 502, 504],
    method_whitelist=("GET", "POST")
):
    session = requests.Session()
    
    retry_strategy = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        method_whitelist=method_whitelist,
        raise_on_status=True
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session

def download_mp3(url, file_name):
    try:
        # session = create_session_with_retries()
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(response.content)
    except requests.exceptions.InvalidURL as err:
        raise requests.exceptions.InvalidURL("Provided url is invalid.")
    except requests.exceptions.RequestException as err:
        raise requests.exceptions.RequestException(f"Request failed: {err}")

def map_value(value, lowest_value, max_value):
        return (value * max_value) + lowest_value
    
def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"🗑️  file '{file_path}' deleted...")
    except OSError as e:
        print(f"Error deleting file '{file_path}': {e}")

def get_necessary_fields_from_payload(payload: Dict[str, str]):
    user_id = payload['user_id']
    email = payload['email']
    record_id = payload['record_id']
    audio_url = payload['audio_url']
    script_id = payload['script_id']
    given_transcription = payload['given_transcription']
    name = payload['name']
    no_of_retries = payload['no_of_retries']

    return RequiredFieldsScriptReading(
        name=name,
        record_id=record_id,
        user_id=user_id,
        email=email,
        given_transcription=given_transcription,
        audio_url=audio_url,
        script_id=script_id,
        no_of_retries=no_of_retries
    )