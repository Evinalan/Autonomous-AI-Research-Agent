
from src.comparison.research_comparator import (
    compare_research_topics
)


if __name__ == "__main__":

    print("Testing Gemini Research Comparator...")

    try:

        result = compare_research_topics(
            topic_a="Artificial Intelligence in Healthcare",
            topic_b="Machine Learning in Medical Diagnosis",
            top_k=3
        )

        print("\nTopic A:")
        print(result["topic_a"])

        print("\nTopic B:")
        print(result["topic_b"])

        print("\nResearch Comparison:")
        print(result["comparison"])

        print("\nTopic A sources:")
        print(len(result["sources_a"]))

        print("\nTopic B sources:")
        print(len(result["sources_b"]))

        print("\nComparison test completed.")

    except Exception as error:

        print("\nComparison test failed:")
        print(error)
