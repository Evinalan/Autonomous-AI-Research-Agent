
from functools import lru_cache

from src.workflow.research_workflow import build_research_workflow

from src.verification.citation_mapper import build_source_registry
from src.verification.metadata_verifier import verify_paper_metadata
from src.verification.claim_verifier import verify_generated_text

from src.reporting.report_generator import generate_research_report
from src.storage.research_history import save_research_history
from src.application.paper_pipeline import prepare_research_database


# ------------------------------------------
# STEP 1: BUILD LITERATURE REVIEW
# ------------------------------------------

def build_literature_review(chunks):

    grouped_papers = {}

    for chunk in chunks:
        title = chunk.get("title", "Unknown title")

        if title not in grouped_papers:
            grouped_papers[title] = {
                "authors": chunk.get("authors", []),
                "source": chunk.get("source", "Unknown"),
                "passages": []
            }

        text = chunk.get("text", "").strip()

        if text and text not in grouped_papers[title]["passages"]:
            grouped_papers[title]["passages"].append(text)

    review = ""

    for title, paper in grouped_papers.items():
        review += f"\n{title}\n"

        authors = paper["authors"]

        if isinstance(authors, list):
            authors = ", ".join(authors)

        review += f"Authors: {authors}\n"
        review += f"Database: {paper['source']}\n\n"
        review += "Relevant retrieved passages:\n"

        for passage in paper["passages"]:
            review += passage + "\n\n"

    return review


# ------------------------------------------
# STEP 2: VERIFY PAPER METADATA
# ------------------------------------------

def verify_sources(sources):

    metadata_results = []

    for source in sources:
        try:
            verification = verify_paper_metadata(source)

        except Exception as error:
            verification = {
                "status": "api_error",
                "message": str(error),
                "metadata": None
            }

        metadata_results.append({
            "source": source,
            "result": verification
        })

    return metadata_results


# ------------------------------------------
# STEP 3: CREATE VERIFICATION NOTES
# ------------------------------------------

def create_verification_notes(metadata_results):

    notes = ""

    for index, item in enumerate(metadata_results, start=1):
        source = item["source"]
        verification = item["result"]

        notes += (
            f"Source {index}: "
            f"{source.get('title', 'Unknown title')}\n"
        )

        notes += (
            f"Status: {verification.get('status', 'Unknown')}\n"
        )

        notes += (
            f"Message: {verification.get('message', '')}\n\n"
        )

    return notes


# ------------------------------------------
# STEP 4: CACHE RESEARCH WORKFLOW
# ------------------------------------------

@lru_cache(maxsize=1)
def get_research_workflow():

    print("Initializing research workflow...")

    return build_research_workflow()


# ------------------------------------------
# STEP 5: MAIN RESEARCH FUNCTION
# ------------------------------------------

def run_research(topic, verify_claims=False, progress_callback=None):

    """
    Run the complete research workflow.

    Claim verification is optional to improve speed.
    """

    def report_progress(message):

        print(message)

        if progress_callback:
            progress_callback(message)

    if not topic or not topic.strip():
        raise ValueError("Please enter a research topic.")

    report_progress("Initializing research workflow...")

    topic = topic.strip()

    # STEP 1: RUN RESEARCH DATABASE PIPELINE

    print("\nStarting research workflow...")

    report_progress(
        "Searching for research papers related to your topic..."
    )

    paper_database = prepare_research_database(
        topic,
        max_papers=5
    )

    # STEP 2: GET TOPIC-SPECIFIC FAISS INDEX

    vector_index = paper_database["vector_index"]
    paper_chunks = paper_database["chunks"]

    print(
        "\nPapers collected:",
        len(paper_database["papers"])
    )

    print(
        "Papers successfully processed:",
        paper_database["processed_papers"]
    )

    print(
        "Total chunks generated:",
        len(paper_chunks)
    )

    # STEP 3: INITIALIZE LANGGRAPH WORKFLOW

    workflow = get_research_workflow()

    # STEP 4: PASS INDEX AND CHUNKS INTO LANGGRAPH

    report_progress(
        "Searching relevant passages in the collected research papers..."
    )

    result = workflow.invoke({
        "question": topic,
        "vector_index": vector_index,
        "paper_chunks": paper_chunks
    })

    if not isinstance(result, dict):
        raise RuntimeError(
            "Research workflow returned an invalid result."
        )

    if result.get("error"):
        raise RuntimeError(result["error"])

    chunks = result.get("chunks", [])

    if not chunks:
        raise RuntimeError(
            "No relevant research passages were found."
        )

    report_progress(
        "Research analysis, summary and gap identification completed."
    )

    # STEP 5: BUILD SOURCE REGISTRY

    print("\nBuilding source registry...")

    sources = build_source_registry(chunks)

    # STEP 6: VERIFY PAPER METADATA

    print("\nVerifying paper metadata...")

    report_progress("Verifying research paper metadata...")

    metadata_results = verify_sources(sources)

    # STEP 7: PREPARE GENERATED TEXT

    generated_text = (
        "RESEARCH ANALYSIS\n"
        + result.get("analysis", "")
        + "\n\nRESEARCH SUMMARY\n"
        + result.get("summary", "")
        + "\n\nRESEARCH GAPS\n"
        + result.get("research_gaps", "")
    )

    # STEP 8: OPTIONAL CLAIM VERIFICATION

    if verify_claims:
        report_progress("Verifying generated research claims...")
    else:
        report_progress("Skipping optional claim verification...")

    claim_verification = {
        "verification_status": "not_run",
        "reason": (
            "Claim verification was skipped to improve "
            "response speed. No claims were verified."
        ),
        "claims": []
    }

    if verify_claims:

        print("\nStarting claim verification...")

        try:
            claim_verification = verify_generated_text(
                generated_text,
                result.get("context", "")
            )

        except Exception as error:
            claim_verification = {
                "verification_status": "manual_review_required",
                "reason": str(error),
                "claims": []
            }

    # STEP 9: PREPARE REPORT CONTENT

    print("\nPreparing research report...")

    literature_review = build_literature_review(chunks)

    verification_notes = create_verification_notes(
        metadata_results
    )

    report_data = {
        "topic": topic,
        "summary": result.get("summary", ""),

        "introduction": (
            f"This report investigates {topic}. "
            "It presents findings from the research passages "
            "retrieved by the Autonomous AI Research Agent."
        ),

        "literature_review": literature_review,
        "analysis": result.get("analysis", ""),
        "research_gaps": result.get("research_gaps", ""),
        "conclusion": result.get("summary", ""),
        "sources": sources,
        "metadata_results": metadata_results,
        "claim_verification": claim_verification,
        "verification_notes": verification_notes
    }

    # STEP 10: GENERATE PDF

    report_progress("Generating your PDF research report...")

    print("\nGenerating PDF report...")

    pdf_path = generate_research_report(report_data)

    # STEP 11: SAVE RESEARCH HISTORY

    history_id = save_research_history({
        "topic": topic,
        "summary": result.get("summary", ""),
        "analysis": result.get("analysis", ""),
        "literature_review": literature_review,
        "research_gaps": result.get("research_gaps", ""),
        "chunks": chunks,
        "sources": sources,
        "metadata_results": metadata_results,
        "claim_verification": claim_verification,
        "pdf_path": str(pdf_path)
    })

    print("\nResearch completed successfully!")

    report_progress("Research report generated successfully!")

    # STEP 12: RETURN RESULTS TO STREAMLIT

    return {
    "topic": topic,

    # Retrieved passages used in the research report
    "chunks": chunks,

    # Complete topic-specific research database
    "paper_chunks": paper_chunks,

    # Topic-specific FAISS index
    "vector_index": vector_index,

    "sources": sources,
    "summary": result.get("summary", ""),
    "analysis": result.get("analysis", ""),
    "research_gaps": result.get("research_gaps", ""),
    "literature_review": literature_review,
    "metadata_results": metadata_results,
    "claim_verification": claim_verification,
    "pdf_path": str(pdf_path),
    "history_id": history_id
   }
