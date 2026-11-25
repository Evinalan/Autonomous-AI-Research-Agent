
from src.llm.ollama_client import generate_response


def run_analysis_agent(question, context):

    """
    Analyzes research methods, datasets,
    findings and limitations.
    """

    print("\n[ANALYSIS AGENT] Analyzing research papers...")

    prompt = f"""
You are a scientific research analysis agent.

Analyze the research passages provided below.

USER RESEARCH QUESTION:
{question}

RESEARCH CONTEXT:
{context}

Prepare a structured analysis with the following sections:

1. Research objectives
2. Methods and algorithms used
3. Datasets and data sources mentioned
4. Main findings and results
5. Evaluation metrics, if mentioned
6. Limitations identified by the papers

RULES:

- Use only the supplied research passages.
- Do not invent datasets, statistics or results.
- If information is missing, write "Not specified in the provided passages".
- Distinguish findings from your own interpretation.
- Refer to the relevant source numbers such as [SOURCE 1].
"""

    return generate_response(prompt)
