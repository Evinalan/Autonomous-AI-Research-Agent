
from src.comparison.research_comparator import compare_research_topics


topic_a = "CNN for image classification"

topic_b = "Vision Transformers for image classification"


print("\nStarting research comparison...\n")

try:

    result = compare_research_topics(
        topic_a=topic_a,
        topic_b=topic_b,
        top_k=5
    )

    print("=" * 60)
    print("RESEARCH COMPARISON")
    print("=" * 60)

    print("\nTOPIC A:")
    print(result["topic_a"])

    print("\nTOPIC B:")
    print(result["topic_b"])

    print("\nCOMPARISON REPORT:")
    print(result["comparison"])

    print("\nRetrieved passages for Topic A:")
    print(len(result["sources_a"]))

    print("\nRetrieved passages for Topic B:")
    print(len(result["sources_b"]))

except Exception as error:

    print("\nComparison failed:")
    print(error)
