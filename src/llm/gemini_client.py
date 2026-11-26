
import os

import streamlit as st
from google import genai
from google.genai import types


# Keep the model name consistent with your Phase 16.1 test.
MODEL_NAME = "gemini-3.5-flash-lite"


def get_gemini_api_key():
    """Read Gemini API key from environment or Streamlit secrets."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            api_key = None

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY was not found. "
            "Set it in .streamlit/secrets.toml "
            "or in your deployment secrets."
        )

    return api_key


def generate_response(
    prompt,
    num_predict=500,
    temperature=0.2,
    system_instruction=None
):
    """
    Generate a response using Google's Gemini API.

    num_predict is retained for compatibility with the
    previous Ollama client. It maps to max_output_tokens.
    """

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    api_key = get_gemini_api_key()

    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=num_predict,
        system_instruction=system_instruction
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config
        )

        answer = response.text

        if not answer:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return answer

    except Exception as error:
        raise RuntimeError(
            f"Gemini API request failed: {error}"
        ) from error
