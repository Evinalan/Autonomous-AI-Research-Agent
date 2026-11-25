
from src.agents.followup_agent import answer_followup_question


question = "What are the main limitations of the research methods?"


print("\nTesting Follow-up Research Agent...\n")

try:

    result = answer_followup_question(
        question=question,
        top_k=5
    )

    print("=" * 60)
    print("FOLLOW-UP QUESTION")
    print("=" * 60)

    print(result["question"])

    print("\nAI ANSWER")
    print("=" * 60)

    print(result["answer"])

    print("\nRETRIEVED SOURCES:")
    print(len(result["sources"]))

except Exception as error:

    print("\nError:")
    print(error)
