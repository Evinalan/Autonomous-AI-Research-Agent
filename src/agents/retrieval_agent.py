
from src.rag.rag_pipeline import answer_question_with_context


def run_retrieval_agent(question, top_k=5):

    """
    Retrieves relevant research passages
    from the FAISS vector database.
    """

    print("\n[RETRIEVAL AGENT] Searching research papers...")

    result = answer_question_with_context(
        question,
        top_k=top_k
    )

    chunks = result["retrieved_chunks"]

    if not chunks:
        print("[RETRIEVAL AGENT] No relevant passages found.")
        return None

    print(
        f"[RETRIEVAL AGENT] Retrieved {len(chunks)} passages."
    )

    return result
