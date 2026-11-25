
from src.rag.rag_pipeline import answer_question_with_context
from src.llm.answer_generator import generate_research_answer


def main():

    print("=" * 65)
    print("          AUTONOMOUS AI RESEARCH AGENT")
    print("                     PHASE 8")
    print("=" * 65)

    print("\nLocal AI model: llama3.2:3b")
    print("Research database: FAISS")

    while True:

        question = input(
            "\nEnter your research question (or type 'exit'): "
        )

        if question.strip().lower() == "exit":
            print("\nExiting Research Agent...")
            break

        try:

            # STEP 1: Retrieve relevant research passages

            print("\nSTEP 1: Retrieving research passages...")

            result = answer_question_with_context(
                question,
                top_k=5
            )

            chunks = result["retrieved_chunks"]

            if not chunks:
                print("\nNo relevant research passages found.")
                continue

            # STEP 2: Generate answer using local LLM

            print("\nSTEP 2: Generating AI research answer...")

            answer = generate_research_answer(
                question,
                result["context"]
            )

            # STEP 3: Display AI answer

            print("\n" + "=" * 65)
            print("                 AI RESEARCH ANSWER")
            print("=" * 65)

            print(answer)

            # STEP 4: Display retrieved sources

            print("\n" + "=" * 65)
            print("                 RETRIEVED SOURCES")
            print("=" * 65)

            for index, chunk in enumerate(chunks, start=1):

                print(f"\n[SOURCE {index}]")

                print(
                    "Paper:",
                    chunk.get("title", "Unknown")
                )

                print(
                    "Page:",
                    chunk.get("page_number", "Unknown")
                )

                print(
                    "Similarity:",
                    round(
                        chunk.get("similarity_score", 0),
                        4
                    )
                )

            print("\n" + "=" * 65)
            print("             RESEARCH COMPLETE")
            print("=" * 65)

        except Exception as error:

            print("\nAn error occurred:")
            print(error)


if __name__ == "__main__":
    main()
