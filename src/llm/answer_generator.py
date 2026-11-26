
from src.llm.ollama_client import generate_response


def generate_research_answer(question, context):

    """
    Generate an answer using research passages
    retrieved by the RAG system.

    The language model is Gemini.
    """

    prompt = f"""
You are an AI research assistant.

Your task is to answer the user's question
using only the research-paper passages provided below.

IMPORTANT RULES:

1. Use the supplied research context.
2. Do not invent research findings or statistics.
3. If the context does not contain enough information,
   clearly say so.
4. Explain technical concepts in understandable language.
5. Compare findings when multiple papers discuss
   the same topic.
6. Mention the source number when referring to a passage,
   for example [SOURCE 1].
7. Do not claim that a paper proves something if the
   provided passage does not support that claim.

USER QUESTION:

{question}

RESEARCH PAPER CONTEXT:

{context}

Write a clear, structured answer with:

1. Introduction
2. Main findings
3. Explanation
4. Comparison of findings, if applicable
5. Limitations of the available evidence
6. Sources used (source numbers)

Remember: Base your answer on the supplied context.
"""

    print("\nSending research context to Gemini...")

    answer = generate_response(
        prompt,
        num_predict=1000,
        temperature=0.2
    )

    return answer
