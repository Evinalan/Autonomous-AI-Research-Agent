
from src.rag.embedding_generator import generate_query_embedding

from src.rag.vector_store import (
    search_similar_chunks,
    search_chunks_in_memory
)


def retrieve_relevant_chunks(
    question,
    top_k=5,
    vector_index=None,
    chunks=None
):
    """
    Convert the research question into an embedding
    and retrieve relevant research chunks.

    If a topic-specific FAISS index is supplied,
    search that index.

    Otherwise, use the existing saved FAISS index.
    """

    if not question or not question.strip():
        raise ValueError("Please enter a research question.")

    print("\nConverting your question into an embedding...")

    query_embedding = generate_query_embedding(question)

    print("\nSearching the research-paper database...")

    # Dynamic retrieval
    if vector_index is not None and chunks is not None:

        relevant_chunks = search_chunks_in_memory(
            query_embedding,
            vector_index,
            chunks,
            top_k=top_k
        )

    # Legacy retrieval for compatibility
    else:

        relevant_chunks = search_similar_chunks(
            query_embedding,
            top_k=top_k
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

    """
    Retrieve relevant chunks and prepare LLM context.
    """

    relevant_chunks = retrieve_relevant_chunks(
        question,
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
