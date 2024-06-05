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