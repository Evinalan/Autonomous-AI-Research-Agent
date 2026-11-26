
from src.agents.followup_agent import answer_followup_question


if __name__ == "__main__":

    print("Testing Gemini Follow-up Agent...")

    # These are sample passages for testing.
    research_result = {
        "chunks": [
            {
                "chunk_id": "test_chunk_1",
                "paper_id": "test_paper_1",
                "title": "AI in Healthcare",
                "page_number": 1,
                "chunk_number": 1,
                "text": (
                    "Artificial intelligence is used "
                    "in healthcare for medical image "
                    "analysis, disease prediction and "
                    "clinical decision support."
                )
            }
        ]
    }

    conversation_history = [
        {
            "role": "user",
            "content": "What is AI in healthcare?"
        },
        {
            "role": "assistant",
            "content": (
                "AI in healthcare uses computational "
                "methods to support medical tasks."
            )
        }
    ]

    try:

        result = answer_followup_question(
            question="What are its major applications?",
            research_result=research_result,
            conversation_history=conversation_history,
            top_k=5
        )

        print("\nQuestion:")
        print(result["question"])

        print("\nAnswer:")
        print(result["answer"])

        print("\nNumber of source passages:")
        print(len(result["sources"]))

        print("\nFollow-up agent test completed.")

    except Exception as error:

        print("\nFollow-up agent test failed:")
        print(error)
