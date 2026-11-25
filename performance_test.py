
import time

from src.rag.rag_pipeline import retrieve_relevant_chunks


def measure_retrieval():

    question = "Deep learning for image classification"

    start_time = time.perf_counter()

    chunks = retrieve_relevant_chunks(
        question,
        top_k=5
    )

    end_time = time.perf_counter()

    elapsed = end_time - start_time

    print("\nPERFORMANCE RESULTS")
    print("-" * 40)

    print("Operation: FAISS retrieval")
    print("Retrieved passages:", len(chunks))
    print("Execution time:", round(elapsed, 3), "seconds")


if __name__ == "__main__":

    measure_retrieval()
