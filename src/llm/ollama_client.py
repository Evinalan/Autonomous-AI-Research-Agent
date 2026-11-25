
import json
import urllib.request
import urllib.error


OLLAMA_URL = "http://localhost:11434/api/chat"

MODEL_NAME = "llama3.2:3b"
def check_ollama_connection():

    url = "http://localhost:11434/api/tags"

    request = urllib.request.Request(
        url,
        method="GET"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=5
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        models = [
            model.get("name", "")
            for model in data.get("models", [])
        ]

        return {
            "available": True,
            "models": models
        }

    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError
    ) as error:

        return {
            "available": False,
            "models": [],
            "error": str(error)
        }


def generate_response(
    prompt,
    num_predict=500,
    temperature=0.2
):
    """
    Send a prompt to Ollama and generate a response.

    Optimizations:
    1. Keep the model loaded for 10 minutes.
    2. Limit unnecessary response generation.
    3. Use a consistent temperature.
    """

    payload = {
        "model": MODEL_NAME,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],

        "stream": False,

        # Keep the model in memory between requests.
        "keep_alive": "10m",

        "options": {
            "num_predict": num_predict,
            "temperature": temperature,
            "num_ctx": 4096
        }
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=600
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        return result["message"]["content"]

    except urllib.error.HTTPError as error:

        error_details = error.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"Ollama HTTP error {error.code}: "
            f"{error_details}"
        )

    except urllib.error.URLError as error:

        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is installed and running. "
            f"Details: {error.reason}"
        )

    except (KeyError, json.JSONDecodeError) as error:

        raise RuntimeError(
            f"Could not read Ollama's response: {error}"
        )
