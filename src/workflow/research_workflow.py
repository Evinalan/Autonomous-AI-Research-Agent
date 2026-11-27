
from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END

from src.agents.retrieval_agent import run_retrieval_agent
from src.agents.citation_agent import run_citation_agent

from src.llm.gemini_client import generate_response


# =====================================================
# RESEARCH WORKFLOW STATE
# =====================================================

class ResearchState(TypedDict, total=False):

    question: str

    # Dynamic topic-specific FAISS index
    vector_index: Any

    # Chunks generated from downloaded research papers
    paper_chunks: list

    # Retrieval information
    retrieval_result: dict
    chunks: list
    context: str

    # Research outputs
    analysis: str
    summary: str
    research_gaps: str
    citations: list

    # Error information
    error: str


# =====================================================
# NODE 1: RETRIEVAL AGENT
# =====================================================

def retrieval_node(state: ResearchState):

    print("\n========== RETRIEVAL AGENT ==========")

    question = state.get("question", "").strip()

    vector_index = state.get("vector_index")

    paper_chunks = state.get("paper_chunks", [])

    if not question:

        return {
            "retrieval_result": {},
            "chunks": [],
            "context": "",
            "error": "Research question is empty."
        }

    if vector_index is None or not paper_chunks:

        return {
            "retrieval_result": {},
            "chunks": [],
            "context": "",
            "error": "Dynamic research database is unavailable."
        }

    try:

        result = run_retrieval_agent(
            question,
            top_k=5,
            vector_index=vector_index,
            chunks=paper_chunks
        )

        if not result:

            return {
                "retrieval_result": {},
                "chunks": [],
                "context": ""
            }

        retrieved_chunks = result.get(
            "retrieved_chunks",
            []
        )

        context = result.get(
            "context",
            ""
        )

        print(
            "Retrieved passages:",
            len(retrieved_chunks)
        )

        return {
            "retrieval_result": result,
            "chunks": retrieved_chunks,
            "context": context
        }

    except Exception as error:

        print("Retrieval agent failed:", error)

        return {
            "retrieval_result": {},
            "chunks": [],
            "context": "",
            "error": str(error)
        }


# =====================================================
# NODE 2: COMBINED RESEARCH AGENT
# =====================================================

def combined_research_node(state: ResearchState):

    print("\n========== COMBINED RESEARCH AGENT ==========")

    question = state.get("question", "")

    context = state.get("context", "")

    if not context.strip():

        return {
            "analysis": "",
            "summary": "",
            "research_gaps": (
                "Research gaps could not be identified "
                "because no relevant research context "
                "was retrieved."
            ),
            "error": "Research context is empty."
        }

    prompt = f"""
You are an academic research assistant.

Research question:
{question}

Research context:
{context}

Your task is to analyze the supplied research passages.

IMPORTANT INSTRUCTIONS:

1. Use ONLY the supplied research context.
2. Do not invent research findings.
3. Do not invent paper titles or authors.
4. Do not invent citations or experimental results.
5. Clearly distinguish evidence from interpretation.
6. If the context is insufficient, explain the limitation.

Prepare your response using these exact headings:

RESEARCH ANALYSIS:

Provide a detailed analysis of the research findings.

RESEARCH SUMMARY:

Summarize the most important findings.

RESEARCH GAPS:

Identify possible research gaps based on the supplied
research passages.

If the supplied passages do not contain enough
information to identify a research gap, explain
that limitation instead of inventing one.
"""

    try:

        response = generate_response(
            prompt,
            num_predict=1200,
            temperature=0.2
        )

        if not response or not response.strip():

            raise ValueError(
                "The LLM returned an empty response."
            )

        response = response.strip()

    except Exception as error:

        print("Research generation failed:", error)

        return {
            "analysis": "",
            "summary": "",
            "research_gaps": "",
            "error": f"Research generation failed: {error}"
        }

    # -------------------------------------------------
    # Extract generated sections
    # -------------------------------------------------

    analysis_marker = "RESEARCH ANALYSIS:"

    summary_marker = "RESEARCH SUMMARY:"

    gaps_marker = "RESEARCH GAPS:"

    analysis_start = response.find(analysis_marker)

    summary_start = response.find(summary_marker)

    gaps_start = response.find(gaps_marker)

    if (
        analysis_start != -1
        and summary_start != -1
        and gaps_start != -1
        and analysis_start < summary_start < gaps_start
    ):

        analysis = response[
            analysis_start + len(analysis_marker):
            summary_start
        ].strip()

        summary = response[
            summary_start + len(summary_marker):
            gaps_start
        ].strip()

        gaps = response[
            gaps_start + len(gaps_marker):
        ].strip()

    else:

        print(
            "Warning: Could not separate all generated sections."
        )

        analysis = response

        summary = (
            "A separate summary could not be extracted. "
            "Refer to the research analysis."
        )

        gaps = (
            "Research gaps could not be extracted separately. "
            "Manual review is recommended."
        )

    print("Research analysis generated.")
    print("Research summary generated.")
    print("Research gaps generated.")

    return {
        "analysis": analysis,
        "summary": summary,
        "research_gaps": gaps
    }


# =====================================================
# NODE 3: CITATION AGENT
# =====================================================

def citation_node(state: ResearchState):

    print("\n========== CITATION AGENT ==========")

    chunks = state.get("chunks", [])

    if not chunks:

        return {
            "citations": []
        }

    try:

        citations = run_citation_agent(chunks)

        print(
            "Citations generated:",
            len(citations) if citations else 0
        )

        return {
            "citations": citations or []
        }

    except Exception as error:

        print("Citation agent failed:", error)

        return {
            "citations": [],
            "error": f"Citation generation failed: {error}"
        }


# =====================================================
# CONDITIONAL ROUTING
# =====================================================

def route_after_retrieval(state: ResearchState):

    if state.get("chunks"):

        return "continue"

    return "stop"


# =====================================================
# NODE 4: NO RESULTS
# =====================================================

def no_results_node(state: ResearchState):

    existing_error = state.get("error", "")

    return {
        "error": (
            existing_error
            or
            "No relevant research passages were found. "
            "Try another research question or collect "
            "more research papers."
        )
    }


# =====================================================
# BUILD LANGGRAPH WORKFLOW
# =====================================================

def build_research_workflow():

    workflow = StateGraph(ResearchState)

    # Register nodes

    workflow.add_node(
        "retrieval",
        retrieval_node
    )

    workflow.add_node(
        "combined_research",
        combined_research_node
    )

    workflow.add_node(
        "citations",
        citation_node
    )

    workflow.add_node(
        "no_results",
        no_results_node
    )

    # Starting point

    workflow.add_edge(
        START,
        "retrieval"
    )

    # Conditional routing

    workflow.add_conditional_edges(
        "retrieval",
        route_after_retrieval,
        {
            "continue": "combined_research",
            "stop": "no_results"
        }
    )

    # Research generation -> citations

    workflow.add_edge(
        "combined_research",
        "citations"
    )

    # End points

    workflow.add_edge(
        "citations",
        END
    )

    workflow.add_edge(
        "no_results",
        END
    )

    print("\nResearch workflow compiled successfully.")

    return workflow.compile()
