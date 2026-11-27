
from src.rag.rag_pipeline import answer_question_with_context


def run_retrieval_agent(
    question,
    top_k=5,
    vector_index=None,
    chunks=None
):

    print("\n[RETRIEVAL AGENT] Searching research papers...")

    result = answer_question_with_context(
        question,
        top_k=top_k,
        vector_index=vector_index,
        chunks=chunks
    )

    retrieved_chunks = result["retrieved_chunks"]

    if not retrieved_chunks:

        print(
            "[RETRIEVAL AGENT] No relevant passages found."
        )

        return None

    print(
        f"[RETRIEVAL AGENT] Retrieved "
        f"{len(retrieved_chunks)} relevant passages."
    )

    return result
