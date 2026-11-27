
import requests
import time


def get_with_retries(url, params, timeout=45):
    """
    Send an API request with limited retries.

    - HTTP 429: Skip this API instead of repeatedly retrying.
    - Timeout/connection errors: Retry up to 3 times.
    - Other HTTP errors: Return None.
    """

    max_retries = 3

    for attempt in range(max_retries):

        response = None

        try:
            response = requests.get(
                url,
                params=params,
                timeout=timeout,
                headers={
                    "User-Agent": "Autonomous-AI-Research-Agent/1.0"
                }
            )

            # Stop immediately if the API rate limit is reached.
            if response.status_code == 429:
                print(
                    f"Rate limit reached for {url}. "
                    "Skipping this API for now."
                )
                response.close()
                return None

            response.raise_for_status()

            return response

        except requests.exceptions.Timeout as error:

            print("API request timed out:", error)

        except requests.exceptions.HTTPError as error:

            print("API returned an HTTP error:", error)

            if response is not None:
                response.close()

            return None

        except requests.exceptions.RequestException as error:

            print("API connection failed:", error)

        finally:
            # Close unsuccessful responses.
            if response is not None and (
                response.status_code >= 400
            ):
                response.close()

        if attempt < max_retries - 1:

            wait_time = 5 * (attempt + 1)

            print(
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)

        else:
            print("Maximum API retries reached.")

    return None
