
from src.workflow.research_workflow import build_research_workflow

from src.verification.citation_mapper import (
    build_source_registry,
    display_source_registry
)

from src.verification.metadata_verifier import (
    verify_paper_metadata
)

from src.verification.claim_verifier import (
    verify_generated_text,
    display_claim_verification
)



def display_metadata_results(sources):

    print("\n" + "=" * 65)
    print("              DOI METADATA VERIFICATION")
    print("=" * 65)

    for paper in sources:

        result = verify_paper_metadata(paper)

        print("\nPaper:", paper.get("title", "Unknown"))

        print("Status:", result.get("status"))

        print("Message:", result.get("message"))

        metadata = result.get("metadata")

        if metadata:

            print("Crossref DOI:", metadata.get("doi", "Not available"))

            print("Crossref Title:", metadata.get("title", "Not available"))

            print("Authors:", metadata.get("authors", []))

            print("Publication year:", metadata.get("year", "Unknown"))

            print("Publisher:", metadata.get("publisher", "Unknown"))

        if "similarity" in result:

            print(
                "Title similarity:",
                result.get("similarity")
            )

        if "title_match" in result:

            print(
                "Title match:",
                result.get("title_match")
            )


def main():

    print("=" * 65)
    print("          AUTONOMOUS AI RESEARCH AGENT")
    print("                    PHASE 11")
    print("        SOURCE VERIFICATION SYSTEM")
    print("=" * 65)

    question = input(
        "\nEnter your research topic: "
    ).strip()

    if not question:
        print("Please enter a research topic.")
        return

    try:

        # STEP 1: Run the existing LangGraph workflow

        print("\nSTEP 1: Running multi-agent research workflow...")

        app = build_research_workflow()

        result = app.invoke({
            "question": question
        })

        if result.get("error"):

            print("\nResearch workflow stopped.")
            print(result["error"])
            return

        # STEP 2: Collect generated research content

        analysis = result.get("analysis", "")
        summary = result.get("summary", "")
        gaps = result.get("research_gaps", "")

        generated_text = f"""
RESEARCH ANALYSIS:

{analysis}

RESEARCH SUMMARY:

{summary}

RESEARCH GAPS:

{gaps}
"""

        # STEP 3: Build source registry

        print("\nSTEP 2: Building source registry...")

        chunks = result.get("chunks", [])

        sources = build_source_registry(chunks)

        display_source_registry(sources)

        # STEP 4: Verify DOI metadata

        print("\nSTEP 3: Verifying paper metadata...")

        display_metadata_results(sources)

        # STEP 5: Verify generated claims

        print("\nSTEP 4: Verifying generated research claims...")

        context = result.get("context", "")

        verification = verify_generated_text(
            generated_text,
            context
        )

        display_claim_verification(verification)

        # STEP 6: Final status

        print("\n" + "=" * 65)
        print("          PHASE 11 VERIFICATION COMPLETE")
        print("=" * 65)

        print("Unique research papers:", len(sources))

        print(
            "Claim verification:",
            verification.get("verification_status")
        )

        print(
            "DOI lookups attempted:",
            sum(
                1 for source in sources
                if source.get("doi")
                or source.get("paper_url")
                or source.get("paper_id")
            )
        )

    except Exception as error:

        print("\nAn error occurred:")
        print(error)


if __name__ == "__main__":
    main()
