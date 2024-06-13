import requests
from functools import wraps
from time import sleep 

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

def download_mp3(url, file_name):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                return True
        except FileNotFoundError as err:
            return False
            raise FileNotFoundError(f"Downloading fail at {url}: ", err)

def map_value(value, lowest_value, max_value):
        return (value * max_value) + lowest_value
    