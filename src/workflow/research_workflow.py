
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from src.agents.retrieval_agent import run_retrieval_agent
from src.agents.citation_agent import run_citation_agent
from src.llm.ollama_client import generate_response


class ResearchState(TypedDict, total=False):

    question: str

    retrieval_result: dict
    chunks: list
    context: str

    analysis: str
    summary: str
    research_gaps: str

    citations: list

    error: str


# ------------------------------------------
# STEP 1: RETRIEVAL NODE
# ------------------------------------------

def retrieval_node(state: ResearchState):

    print("\nRETRIEVAL AGENT STARTED")

    result = run_retrieval_agent(
        state["question"],
        top_k=5
    )

    if not result:

        return {
            "retrieval_result": {},
            "chunks": [],
            "context": ""
        }

    return {
        "retrieval_result": result,
        "chunks": result.get("retrieved_chunks", []),
        "context": result.get("context", "")
    }


# ------------------------------------------
# STEP 2: COMBINED AI RESEARCH NODE
# ------------------------------------------

def combined_research_node(state: ResearchState):

    print("\nCOMBINED RESEARCH AGENT STARTED")

    question = state["question"]
    context = state["context"]

    prompt = f"""
You are an academic research assistant.

Answer the research question using ONLY the supplied research context.

RESEARCH QUESTION:
{question}

RESEARCH CONTEXT:
{context}

Prepare three sections.

SECTION 1: RESEARCH ANALYSIS

Explain:
- Main research findings
- Important methods and techniques
- Datasets or experiments mentioned
- Important results
- Limitations

Use source numbers such as [SOURCE 1] whenever possible.

SECTION 2: RESEARCH SUMMARY

Provide:
- An overview of the research topic
- Main themes found in the retrieved papers
- Important conclusions

SECTION 3: RESEARCH GAPS

Identify:
- Limitations explicitly mentioned in the papers
- Missing research areas
- Possible future research directions

Clearly distinguish explicitly stated limitations from your own inferred suggestions.

IMPORTANT:
- Do not invent research findings.
- Do not invent paper titles or citations.
- If information is unavailable, say so.
- Keep the answer concise but informative.
- Use the exact section headings below.

RESEARCH ANALYSIS:
[Your analysis]

RESEARCH SUMMARY:
[Your summary]

RESEARCH GAPS:
[Your research gaps]
"""

    response = generate_response(
        prompt,
        num_predict=1200,
        temperature=0.2
    )

    # Extract the three sections.

    analysis = ""
    summary = ""
    gaps = ""

    try:

        analysis_marker = "RESEARCH ANALYSIS:"
        summary_marker = "RESEARCH SUMMARY:"
        gaps_marker = "RESEARCH GAPS:"

        analysis_start = response.find(analysis_marker)
        summary_start = response.find(summary_marker)
        gaps_start = response.find(gaps_marker)

        if analysis_start != -1 and summary_start != -1:

            analysis = response[
                analysis_start + len(analysis_marker):summary_start
            ].strip()

        if summary_start != -1 and gaps_start != -1:

            summary = response[
                summary_start + len(summary_marker):gaps_start
            ].strip()

        if gaps_start != -1:

            gaps = response[
                gaps_start + len(gaps_marker):
            ].strip()

        # Fallback if the model does not follow the format.

        if not analysis:
            analysis = response

        if not summary:
            summary = "Summary could not be separated from the generated response."

        if not gaps:
            gaps = "Research gaps could not be separated from the generated response."

    except Exception:

        analysis = response
        summary = "Could not extract summary separately."
        gaps = "Could not extract research gaps separately."

    print("COMBINED RESEARCH AGENT COMPLETED")

    return {
        "analysis": analysis,
        "summary": summary,
        "research_gaps": gaps
    }


# ------------------------------------------
# STEP 3: CITATION NODE
# ------------------------------------------

def citation_node(state: ResearchState):

    print("\nCITATION AGENT STARTED")

    citations = run_citation_agent(
        state.get("chunks", [])
    )

    return {
        "citations": citations
    }


# ------------------------------------------
# STEP 4: ROUTING
# ------------------------------------------

def route_after_retrieval(state: ResearchState):

    if state.get("chunks"):
        return "continue"

    return "stop"


def no_results_node(state: ResearchState):

    return {
        "error": (
            "No relevant research passages were found. "
            "Try another research question or collect more papers."
        )
    }


# ------------------------------------------
# STEP 5: BUILD WORKFLOW
# ------------------------------------------

def build_research_workflow():

    workflow = StateGraph(ResearchState)

    workflow.add_node("retrieval", retrieval_node)

    workflow.add_node("combined_research", combined_research_node)

    workflow.add_node("citations", citation_node)

    workflow.add_node("no_results", no_results_node)

    workflow.add_edge(START, "retrieval")

    workflow.add_conditional_edges(
        "retrieval",
        route_after_retrieval,
        {
            "continue": "combined_research",
            "stop": "no_results"
        }
    )

    workflow.add_edge(
        "combined_research",
        "citations"
    )

    workflow.add_edge("citations", END)

    workflow.add_edge("no_results", END)

    return workflow.compile()
