
from src.rag.embedding_generator import generate_query_embedding
from src.rag.vector_store import search_similar_chunks


def retrieve_relevant_chunks(question, top_k=5):
    """
    Convert the user's question into an embedding
    and retrieve the most relevant research-paper chunks.
    """

    if not question or not question.strip():
        raise ValueError("Please enter a research question.")

    print("\nConverting your question into an embedding...")

    query_embedding = generate_query_embedding(question)

    print("Searching the research-paper database...")

    relevant_chunks = search_similar_chunks(
        query_embedding,
        top_k=top_k
    )

    return relevant_chunks


def build_context(relevant_chunks):
    """
    Combine retrieved chunks into context
    that can be supplied to a local LLM.
    """

    if not relevant_chunks:
        return "No relevant research passages were found."

    context = ""

    for index, chunk in enumerate(relevant_chunks, start=1):

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


def answer_question_with_context(question, top_k=5):
    """
    Phase 7 RAG pipeline:
    1. Retrieve relevant chunks.
    2. Build context from those chunks.
    3. Return the context for a future LLM.
    """

    relevant_chunks = retrieve_relevant_chunks(
        question,
        top_k=top_k
    )

    context = build_context(relevant_chunks)

    return {
        "question": question,
        "retrieved_chunks": relevant_chunks,
        "context": context
    }
