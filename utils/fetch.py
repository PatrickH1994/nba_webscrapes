import requests
import time
import random

def fetch_url(url, callback, callback_args):
    with requests.Session() as session:  # Manage session within a context manager
        backoff_time = 5  # Initial backoff time
        max_backoff_time = 60  # Maximum backoff time
        for attempt in range(5):  # Retry up to 5 times
            response = session.get(url)
            if response.status_code == 429:
                return 429
                retry_after = int(response.headers.get('Retry-After', backoff_time))  # Use backoff_time if header is missing
                print(f'Rate limited. Retrying in {retry_after} seconds...')
                time.sleep(retry_after)
                backoff_time = min(backoff_time * 2, max_backoff_time)  # Double the backoff_time, but do not exceed max_backoff_time
            elif response.status_code == 200:
                try:
                    return callback(response, *callback_args)
                except Exception as e:
                    print(f'Failed to process the page: {e} --> {url}')
                    time.sleep(backoff_time)
                    backoff_time = min(backoff_time * 2, max_backoff_time)  # Double the backoff_time, but do not exceed max_backoff_time
            else:
                if response.status_code == 404:
                    print(f"404 encountered for URL: {url}. Skipping.")
                    return None
                print(f'Failed with status {response.status_code} for URL: {url}. Retrying in {backoff_time} seconds...')
                time.sleep(backoff_time)
                backoff_time = min(backoff_time * 2, max_backoff_time)  # Double the backoff_time, but do not exceed max_backoff_time

            # Random delay to avoid being blocked, executed regardless of the response status
            time.sleep(random.uniform(2, 5))  # Reduced random sleep time to speed up the retry process
