
import os
import time

import streamlit as st
from google import genai
from google.genai import types, errors


# Gemini model
MODEL_NAME = "gemini-3.5-flash-lite"

# Additional application-level attempts
MAX_ATTEMPTS = 2


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

    num_predict maps to max_output_tokens.

    The temperature argument is retained for compatibility
    with existing project code. Gemini 3.5 Flash-Lite
    does not support custom temperature values.
    """

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    api_key = get_gemini_api_key()

    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        max_output_tokens=num_predict,
        system_instruction=system_instruction
    )

    retryable_codes = {
        408,
        429,
        500,
        502,
        503,
        504
    }

    try:

        for attempt in range(MAX_ATTEMPTS):

            try:

                print(
                    f"\nGemini request attempt "
                    f"{attempt + 1}/{MAX_ATTEMPTS}"
                )

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

                print("Gemini response generated successfully.")

                return answer

            except errors.APIError as error:

                status_code = getattr(
                    error,
                    "code",
                    None
                )

                if (
                    status_code in retryable_codes
                    and attempt < MAX_ATTEMPTS - 1
                ):

                    wait_time = 2 ** (attempt + 1)

                    print(
                        f"Gemini temporary error "
                        f"({status_code}). "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                    continue

                raise RuntimeError(
                    f"Gemini API request failed: {error}"
                ) from error

        raise RuntimeError(
            "Gemini could not generate a response "
            "after the retry attempts."
        )

    finally:
        client.close()
