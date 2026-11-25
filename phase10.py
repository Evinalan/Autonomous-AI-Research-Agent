
from src.workflow.research_workflow import build_research_workflow

from src.agents.citation_agent import display_citations


def main():

    print("=" * 65)
    print("          AUTONOMOUS AI RESEARCH AGENT")
    print("                    PHASE 10")
    print("              LANGGRAPH WORKFLOW")
    print("=" * 65)

    question = input(
        "\nEnter your research topic: "
    ).strip()

    if not question:
        print("Please enter a research topic.")
        return

    try:

        # Build LangGraph workflow
        app = build_research_workflow()

        # Initial shared state
        initial_state = {
            "question": question
        }

        print("\nStarting multi-agent workflow...")

        # Execute workflow
        result = app.invoke(initial_state)

        # Check for retrieval failure
        if result.get("error"):

            print("\nWORKFLOW STOPPED")
            print(result["error"])
            return

        # Display research analysis
        print("\n" + "=" * 65)
        print("                  RESEARCH ANALYSIS")
        print("=" * 65)

        print(result.get("analysis", "No analysis available."))

        # Display summary
        print("\n" + "=" * 65)
        print("                  RESEARCH SUMMARY")
        print("=" * 65)

        print(result.get("summary", "No summary available."))

        # Display research gaps
        print("\n" + "=" * 65)
        print("                  RESEARCH GAPS")
        print("=" * 65)

        print(
            result.get(
                "research_gaps",
                "No research gaps available."
            )
        )

        # Display citations
        print("\n" + "=" * 65)
        print("                  RESEARCH CITATIONS")
        print("=" * 65)

        display_citations(
            result.get("citations", [])
        )

        print("\n" + "=" * 65)
        print("          LANGGRAPH WORKFLOW COMPLETED")
        print("=" * 65)

    except Exception as error:

        print("\nAn error occurred during workflow execution:")
        print(error)


if __name__ == "__main__":
    main()
