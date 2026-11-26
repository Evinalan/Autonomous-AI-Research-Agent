
import streamlit as st

from src.llm.gemini_client import generate_response


st.set_page_config(
    page_title="Gemini API Test",
    page_icon="🤖"
)

st.title("Gemini API Connection Test")

st.write(
    "Testing whether the cloud AI model "
    "can generate research-related responses."
)

if st.button("Test Gemini API"):

    with st.spinner("Connecting to Gemini..."):

        try:

            response = generate_response(
                prompt=(
                    "Explain what a research gap is "
                    "in academic research in 5 sentences."
                )
            )

            st.success("Gemini API connected successfully!")

            st.subheader("Gemini Response")

            st.write(response)

        except Exception as error:

            st.error(str(error))
