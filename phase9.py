
from src.agents.retrieval_agent import run_retrieval_agent

from src.agents.analysis_agent import run_analysis_agent

from src.agents.summarization_agent import run_summarization_agent

from src.agents.research_gap_agent import run_research_gap_agent

from src.agents.citation_agent import (
    run_citation_agent,
    display_citations
)


def main():

    print("=" * 65)
    print("          AUTONOMOUS AI RESEARCH AGENT")
    print("                     PHASE 9")
    print("=" * 65)

    question = input(
        "\nEnter your research topic: "
    ).strip()

    if not question:
        print("Please enter a research topic.")
        return

    # AGENT 1: RETRIEVAL

    retrieval_result = run_retrieval_agent(
        question,
        top_k=5
    )

    if not retrieval_result:
        print("\nNo research context available.")
        return

    context = retrieval_result["context"]

    chunks = retrieval_result["retrieved_chunks"]

    # AGENT 2: RESEARCH ANALYSIS

    analysis = run_analysis_agent(
        question,
        context
    )

    print("\n" + "=" * 65)
    print("             RESEARCH ANALYSIS")
    print("=" * 65)

    print(analysis)

    # AGENT 3: SUMMARIZATION

    summary = run_summarization_agent(
        question,
        context
    )

    print("\n" + "=" * 65)
    print("             RESEARCH SUMMARY")
    print("=" * 65)

    print(summary)

    # AGENT 4: RESEARCH GAP IDENTIFICATION

    gaps = run_research_gap_agent(
        question,
        context
    )

    print("\n" + "=" * 65)
    print("             RESEARCH GAPS")
    print("=" * 65)

    print(gaps)

    # AGENT 5: CITATION MANAGEMENT

    citations = run_citation_agent(chunks)

    display_citations(citations)

    print("\n" + "=" * 65)
    print("        PHASE 9 RESEARCH PROCESS COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    main()
