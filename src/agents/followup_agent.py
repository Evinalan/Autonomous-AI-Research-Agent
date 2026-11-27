
from src.rag.rag_pipeline import (
    retrieve_relevant_chunks,
    build_context
)

from src.llm.gemini_client import generate_response


def answer_followup_question(
    question,
    research_result=None,
    conversation_history=None,
    top_k=5
):
    """
    Answer a follow-up question using:

    1. Previously retrieved research passages.
    2. New passages retrieved from FAISS.
    3. Conversation history.
    4. Gemini cloud AI model.
    """

    if not question or not question.strip():
        raise ValueError("Please enter a follow-up question.")

    question = question.strip()

    conversation_history = conversation_history or []

    # Retrieve additional passages relevant to the question.
    # Reuse the original topic-specific FAISS database.
    vector_index = (
    research_result.get("vector_index")
    if research_result else None
    )

    paper_chunks = (
    research_result.get("paper_chunks", [])
    if research_result else []
    )

    if vector_index is not None and paper_chunks:

      new_chunks = retrieve_relevant_chunks(
        question,
        top_k=top_k,
        vector_index=vector_index,
        chunks=paper_chunks
       )

    else:
    # Older saved research history may not contain
    # the original in-memory FAISS index.
    # Avoid retrieving unrelated passages from an old index.
       new_chunks = []

    # Get passages saved with the completed research report.
    previous_chunks = []

    if research_result:
        previous_chunks = research_result.get("chunks", [])

    # Combine previous and newly retrieved passages.
    combined_chunks = []
    seen_chunks = set()

    for chunk in previous_chunks + new_chunks:

        chunk_key = (
            chunk.get("chunk_id")
            or (
                chunk.get("paper_id"),
                chunk.get("page_number"),
                chunk.get("chunk_number"),
                chunk.get("text", "")[:150]
            )
        )

        if chunk_key not in seen_chunks:
            seen_chunks.add(chunk_key)
            combined_chunks.append(chunk)

    if not combined_chunks:
        raise ValueError(
            "No research passages are available. "
            "Run research first or check your FAISS database."
        )

    # Keep context within a manageable size.
    selected_chunks = combined_chunks[:10]

    context = build_context(selected_chunks)

    # Build a short conversation history for Gemini.
    history_text = []

    for message in conversation_history[-6:]:

        role = message.get("role", "")

        content = message.get("content", "")

        if role in ("user", "assistant") and content:

            history_text.append(
                f"{role.upper()}: {content}"
            )

    conversation_context = "\n\n".join(history_text)

    system_prompt = """
You are an academic research follow-up assistant.

Answer questions using the supplied research passages.

Rules:

1. Use the supplied research evidence.
2. Do not invent authors, papers, datasets or results.
3. Cite supporting passages using references such as [SOURCE 1].
4. If the evidence is insufficient, clearly say so.
5. Distinguish established findings from your own interpretations.
6. Explain technical concepts clearly when asked.
7. Use conversation history to understand follow-up questions.
8. Do not treat earlier AI-generated answers as verified research evidence.
9. Give clear and structured answers.
"""

    user_prompt = f"""
PREVIOUS CONVERSATION:

{conversation_context}

RESEARCH PASSAGES:

{context}

FOLLOW-UP QUESTION:

{question}

Answer the question using the supplied research passages.
Include source references wherever possible.
"""

    try:

        answer = generate_response(
            prompt=user_prompt,
            system_instruction=system_prompt,
            num_predict=1000,
            temperature=0.2
        )

        if not answer:
            raise RuntimeError(
                "Gemini returned an empty answer."
            )

        return {
            "question": question,
            "answer": answer,
            "sources": selected_chunks
        }

    except Exception as error:

        raise RuntimeError(
            f"Follow-up question generation failed: {error}"
        ) from error
