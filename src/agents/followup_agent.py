
import json
import urllib.request
import urllib.error

from src.rag.rag_pipeline import (
    retrieve_relevant_chunks,
    build_context
)


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2:3b"


def answer_followup_question(
    question,
    research_result=None,
    conversation_history=None,
    top_k=5
):
    """
    Answer a follow-up question using:
    1. Previously retrieved research passages, when available.
    2. New relevant passages retrieved from FAISS.
    3. The local Ollama model.
    """

    if not question or not question.strip():
        raise ValueError("Please enter a follow-up question.")

    question = question.strip()

    conversation_history = conversation_history or []

    # Retrieve additional passages relevant to the question.
    new_chunks = retrieve_relevant_chunks(
        question,
        top_k=top_k
    )

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

    # Build a short conversation history for the model.
    history_messages = []

    for message in conversation_history[-6:]:

        if message.get("role") in ("user", "assistant"):

            history_messages.append({
                "role": message["role"],
                "content": message.get("content", "")
            })

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
7. Use the conversation history to understand follow-up questions.
8. Do not treat earlier AI-generated answers as verified research evidence.
"""

    user_prompt = f"""
RESEARCH PASSAGES:

{context}

FOLLOW-UP QUESTION:

{question}

Answer the question using the research passages above.
Include source references wherever possible.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(history_messages)

    messages.append({
        "role": "user",
        "content": user_prompt
    })

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }

    request_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=request_data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=600
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        answer = result.get(
            "message", {}
        ).get(
            "content",
            ""
        )

        if not answer:
            raise RuntimeError(
                "Ollama returned an empty answer."
            )

        return {
            "question": question,
            "answer": answer,
            "sources": selected_chunks
        }

    except urllib.error.HTTPError as error:

        details = error.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"Ollama HTTP error {error.code}: {details}"
        )

    except urllib.error.URLError as error:

        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running. "
            f"Details: {error}"
        )

    except TimeoutError:

        raise RuntimeError(
            "Ollama took too long to respond. "
            "Try a shorter question or fewer passages."
        )

    except json.JSONDecodeError as error:

        raise RuntimeError(
            f"Could not decode Ollama response: {error}"
        )
