from src.application.research_service import run_research

topic = "Applications of Artificial Intelligence in Healthcare"

try:
    print("\nStarting research workflow...\n")

    result = run_research(
        topic,
        verify_claims=False
    )

    if not isinstance(result, dict):
        raise RuntimeError("Research workflow returned an invalid result.")

    print("\nResearch workflow completed!")

    print("\nTopic:")
    print(result.get("topic"))

    print("\nSummary:")
    print(result.get("summary", "")[:1000])

    print("\nResearch gaps:")
    print(result.get("research_gaps", "")[:1000])

    print("\nNumber of sources:")
    print(len(result.get("sources", [])))

    print("\nPDF report:")
    print(result.get("pdf_path"))

except Exception as error:
    print("\nResearch workflow failed!")
    print(error)