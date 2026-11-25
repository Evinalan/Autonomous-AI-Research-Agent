
from src.application.research_service import run_research


def main():

    print("=" * 65)
    print("          AUTONOMOUS AI RESEARCH AGENT")
    print("                    PHASE 12")
    print("=" * 65)

    topic = input("\nEnter your research topic: ").strip()

    if not topic:
        print("Research topic cannot be empty.")
        return

    print("\nRunning research workflow...")

    try:

        result = run_research(topic)

        print("\nPHASE 12 COMPLETED!")

        print("Unique papers:", len(result["sources"]))

        print("PDF saved at:", result["pdf_path"])

    except Exception as error:

        print("\nResearch generation failed:")
        print(error)


if __name__ == "__main__":
    main()
