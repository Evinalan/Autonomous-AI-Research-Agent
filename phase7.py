
from src.rag.rag_pipeline import answer_question_with_context


def main():

    print("=" * 60)
    print("       AUTONOMOUS AI RESEARCH AGENT")
    print("                  PHASE 7")
    print("=" * 60)

    print("\nYour research-paper database is ready!")

    while True:

        question = input(
            "\nEnter your research question (or type 'exit'): "
        )

        if question.lower().strip() == "exit":
            print("\nExiting Research Agent...")
            break

        try:

            result = answer_question_with_context(
                question,
                top_k=5
            )

            print("\n" + "=" * 60)
            print("RETRIEVED RESEARCH PASSAGES")
            print("=" * 60)

            chunks = result["retrieved_chunks"]

            if not chunks:
                print("\nNo relevant passages were found.")
                continue

            for index, chunk in enumerate(chunks, start=1):

                print(f"\nSOURCE {index}")
                print("-" * 50)

                print("Paper:", chunk.get("title", "Unknown"))
                print("Page:", chunk.get("page_number", "Unknown"))

                score = chunk.get("similarity_score", 0)
                print(f"Similarity: {score:.4f}")

                print("\nPassage:")
                print(chunk.get("text", "")[:1000])

            print("\n" + "=" * 60)
            print("CONTEXT PREPARED FOR THE LOCAL AI MODEL")
            print("=" * 60)

            print(result["context"][:5000])

        except Exception as error:

            print("\nSomething went wrong:")
            print(error)


if __name__ == "__main__":
    main()
