import requests
import time


if __name__ == "__main__":
    step = 5
    limit = 60 * step
    uri = "http://localhost:8000"

    elapsed = 0
    condition = True

    while condition:
        time.sleep(step)
        elapsed += step

        try:
            response = requests.get(uri)
            data = response.json()
            if "Welcome to the Climate Data API" in data['description']:
                condition = False
                print(f"API ready after {elapsed} seconds")
                print(data)

        except requests.exceptions.ConnectionError:
            print(f"API not ready after {elapsed} seconds")

        if elapsed > limit:
            condition = False

