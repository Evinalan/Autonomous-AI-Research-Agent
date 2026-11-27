
from src.rag.embedding_generator import generate_query_embedding

from src.rag.vector_store import (
    search_similar_chunks,
    search_chunks_in_memory,
    search_diverse_chunks
)



def retrieve_relevant_chunks(
    question,
    top_k=5,
    vector_index=None,
    chunks=None
):
    """
    Retrieve relevant research passages.

    Uses diversified retrieval when a topic-specific
    in-memory FAISS index is provided.
    """

    if not question or not question.strip():
        raise ValueError("Please enter a research question.")

    print("\nConverting your question into an embedding...")

    query_embedding = generate_query_embedding(question)

    if vector_index is not None and chunks is not None:

        print("\nUsing diversified in-memory retrieval...")

        relevant_chunks = search_diverse_chunks(
            query_embedding=query_embedding,
            index=vector_index,
            chunks=chunks,
            top_k=top_k,
            candidates_multiplier=5,
            max_chunks_per_paper=2
        )

    else:

        print("\nUsing persistent FAISS retrieval...")

        relevant_chunks = search_similar_chunks(
            query_embedding=query_embedding,
            top_k=top_k
        )

    print(
        "\nRelevant passages retrieved:",
        len(relevant_chunks)
    )

    return relevant_chunks


def build_context(relevant_chunks):

    """
    Convert retrieved chunks into context for the LLM.
    """

    if not relevant_chunks:
        return "No relevant research passages were found."

    context = ""

    for index, chunk in enumerate(
        relevant_chunks,
        start=1
    ):

        title = chunk.get("title", "Unknown title")

        source = chunk.get("source", "Unknown source")

        page = chunk.get("page_number", "Unknown page")

        score = chunk.get("similarity_score", 0)

        text = chunk.get("text", "")

        context += f"""
[SOURCE {index}]

Paper title: {title}

Source: {source}

Page: {page}

Similarity score: {score:.4f}

Research passage:

{text}

----------------------------------------
"""

    return context


def answer_question_with_context(
    question,
    top_k=5,
    vector_index=None,
    chunks=None
):
    relevant_chunks = retrieve_relevant_chunks(
        question=question,
        top_k=top_k,
        vector_index=vector_index,
        chunks=chunks
    )

    context = build_context(relevant_chunks)

    return {
        "question": question,
        "retrieved_chunks": relevant_chunks,
        "context": context
    }