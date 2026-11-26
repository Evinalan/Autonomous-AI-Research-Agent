from src.llm.gemini_client import generate_response

try:
    response = generate_response(
        prompt="Explain artificial intelligence in three sentences.",
        num_predict=200,
        temperature=0.2
    )

    print("\nGemini API is working!")
    print("\nResponse:")
    print(response)

except Exception as error:
    print("\nGemini API test failed!")
    print(error)