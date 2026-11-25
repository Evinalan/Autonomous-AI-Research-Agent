
import json
import urllib.request
import urllib.error

from src.rag.rag_pipeline import retrieve_relevant_chunks, build_context


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2:3b"


def retrieve_topic_research(topic, top_k=5):
    """
    Retrieve research passages related to one topic
    using the existing FAISS vector database.
    """

    chunks = retrieve_relevant_chunks(
        topic,
        top_k=top_k
    )

    if not chunks:
        return {
            "topic": topic,
            "chunks": [],
            "context": ""
        }

    context = build_context(chunks)

    return {
        "topic": topic,
        "chunks": chunks,
        "context": context
    }


def compare_with_ollama(topic_a, topic_b, context_a, context_b):
    """
    Compare two research topics using the local Ollama model.
    """

    prompt = f"""
You are an academic research comparison assistant.

Compare the following two research topics using ONLY
the supplied research passages.

TOPIC A:
{topic_a}

RESEARCH PASSAGES FOR TOPIC A:
{context_a}

TOPIC B:
{topic_b}

RESEARCH PASSAGES FOR TOPIC B:
{context_b}

Prepare a detailed research comparison using these sections:

# 1. Research Objectives
Explain what each research topic aims to achieve.

# 2. Methodologies
Compare the methods and techniques used.

# 3. Datasets
Compare the datasets mentioned in the supplied passages.
If dataset information is unavailable, say so.

# 4. Key Findings
Compare the findings supported by the supplied passages.

# 5. Limitations
Explain the limitations mentioned in the research.

# 6. Research Gaps
Identify gaps explicitly mentioned in the passages.
Clearly label any additional interpretation as an inference.

# 7. Future Research Opportunities
Suggest possible directions based on the identified gaps.
Label these as suggestions, not established facts.

# 8. Overall Comparison
Explain the main similarities and differences.

# 9. Conclusion
Give a balanced conclusion.

IMPORTANT RULES:
- Do not invent research papers, authors, datasets or results.
- Do not assume information that is not present in the passages.
- If evidence is missing, write "Insufficient evidence in retrieved passages."
- Distinguish documented findings from your own inferences.
- Include source references such as [SOURCE 1] when available.
- Do not claim that one method is better unless the passages support it.
"""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a careful academic research analyst. "
                    "Use only the supplied evidence and identify "
                    "uncertainty clearly."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            result = json.loads(response.read().decode("utf-8"))

        return result.get("message", {}).get(
            "content",
            "The model returned an empty response."
        )

    except urllib.error.URLError as error:
        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running and the model is installed. "
            f"Details: {error}"
        )

    except TimeoutError:
        raise RuntimeError(
            "Ollama took too long to respond. "
            "Try comparing fewer passages."
        )

    except (json.JSONDecodeError, KeyError) as error:
        raise RuntimeError(
            f"Could not read the Ollama response: {error}"
        )


def compare_research_topics(topic_a, topic_b, top_k=5):
    """
    Complete comparison pipeline:
    1. Retrieve passages for topic A.
    2. Retrieve passages for topic B.
    3. Compare both using Ollama.
    4. Return the comparison and source passages.
    """

    if not topic_a or not topic_a.strip():
        raise ValueError("Please enter Research Topic A.")

    if not topic_b or not topic_b.strip():
        raise ValueError("Please enter Research Topic B.")

    if topic_a.strip().lower() == topic_b.strip().lower():
        raise ValueError("Please enter two different research topics.")

    research_a = retrieve_topic_research(
        topic_a.strip(),
        top_k=top_k
    )

    research_b = retrieve_topic_research(
        topic_b.strip(),
        top_k=top_k
    )

    if not research_a["chunks"]:
        raise ValueError(
            f"No research passages were found for Topic A: {topic_a}"
        )

    if not research_b["chunks"]:
        raise ValueError(
            f"No research passages were found for Topic B: {topic_b}"
        )

    comparison = compare_with_ollama(
        topic_a=topic_a,
        topic_b=topic_b,
        context_a=research_a["context"],
        context_b=research_b["context"]
    )

    return {
        "topic_a": topic_a,
        "topic_b": topic_b,
        "comparison": comparison,
        "sources_a": research_a["chunks"],
        "sources_b": research_b["chunks"]
    }
