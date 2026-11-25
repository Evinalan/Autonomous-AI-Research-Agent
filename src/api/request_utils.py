import requests
import time


def get_with_retries(url, params, timeout=30):
    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=timeout,
                headers={
                    "User-Agent": "AI-Research-Agent/1.0"
                }
            )

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")

                try:
                    wait_time = float(retry_after)
                except (TypeError, ValueError):
                    wait_time = 15 * (2 ** attempt)

                response.close()

                if attempt == max_retries - 1:
                    raise requests.exceptions.HTTPError(
                        "API rate limit exceeded after retries."
                    )

                print(f"Rate limit reached. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as error:

            if attempt == max_retries - 1:
                raise

            wait_time = 5 * (2 ** attempt)

            print("Request failed:", error)
            print(f"Retrying in {wait_time} seconds...")

            time.sleep(wait_time)

    return None