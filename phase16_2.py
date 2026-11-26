
from src.llm.answer_generator import generate_research_answer


question = (
    "What are the applications of artificial "
    "intelligence in healthcare?"
)

context = """
[SOURCE 1]

Title: Artificial Intelligence in Healthcare

Passage:
Artificial intelligence is being used in healthcare
for medical image analysis, clinical decision support,
disease prediction and patient monitoring.

[SOURCE 2]

Title: Machine Learning Applications in Medicine

Passage:
Machine learning techniques can help identify
patterns in medical datasets and support
early disease detection.
"""


if __name__ == "__main__":

    print("Testing Gemini through answer_generator.py")

    try:

        answer = generate_research_answer(
            question,
            context
        )

        print("\nGenerated Research Answer:\n")

        print(answer)

        print("\nPhase 16.2 test completed.")

    except Exception as error:

        print("\nTest failed:")
        print(error)
