from src.llm.gemini_client import generate_response


def run_summarization_agent(question, context):

    """
    Produces a concise summary of the retrieved
    research-paper passages.
    """

    print("\n[SUMMARIZATION AGENT] Summarizing research...")

    prompt = f"""
You are a scientific research summarization agent.

Research topic:
{question}

Research passages:
{context}

Create a structured research summary containing:

1. Overview of the research topic
2. Important concepts
3. Techniques and approaches
4. Key findings
5. Common themes across the papers
6. Overall conclusion

RULES:

- Summarize only information supported by the passages.
- Do not invent research findings.
- Mention source numbers where appropriate.
- Use clear and understandable language.
- If the papers disagree, mention the differences.
"""

    return generate_response(prompt)
