from src.llm.gemini_client import generate_response


def run_research_gap_agent(question, context):

    """
    Identifies research limitations and
    potential future research directions.
    """

    print("\n[RESEARCH GAP AGENT] Identifying research gaps...")

    prompt = f"""
You are an academic research gap identification agent.

Research topic:
{question}

Research passages:
{context}

Analyze the provided passages and identify:

1. Limitations explicitly mentioned by the authors
2. Problems with the research methods
3. Dataset limitations
4. Areas that need further investigation
5. Potential future research directions
6. Three possible research questions for future studies

IMPORTANT RULES:

- Separate explicitly stated limitations from your own inferences.
- Support each identified gap with source numbers.
- Do not claim that a gap is new or unexplored across all
  scientific literature based on these passages alone.
- Do not invent missing information.
- If the passages are insufficient, clearly state that.
"""

    return generate_response(prompt)
