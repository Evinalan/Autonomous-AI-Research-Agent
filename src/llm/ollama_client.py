
from src.llm.gemini_client import (
    generate_response as gemini_generate_response,
    get_gemini_api_key,
    MODEL_NAME
)


def check_gemini_connection():
    """
    Check whether a Gemini API key is configured.

    This checks configuration only. It does not make
    a paid or quota-consuming model generation request.
    """

    try:
        get_gemini_api_key()

        return {
            "available": True,
            "models": [MODEL_NAME]
        }

    except Exception as error:

        return {
            "available": False,
            "models": [],
            "error": str(error)
        }


def check_ollama_connection():
    """
    Temporary compatibility alias.

    Existing app imports can continue working until
    the Streamlit status section is updated.
    """

    return check_gemini_connection()


def generate_response(
    prompt,
    num_predict=500,
    temperature=0.2
):
    """
    Compatibility function.

    Existing agents can continue importing
    generate_response from ollama_client.py.

    Actual generation now happens through Gemini.
    """

    return gemini_generate_response(
        prompt=prompt,
        num_predict=num_predict,
        temperature=temperature
    )
