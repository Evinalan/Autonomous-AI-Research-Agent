
from src.api.paper_search import search_all_papers

from src.utils.paper_utils import (
    normalize_paper,
    remove_duplicates,
    sort_papers_by_date
)

from src.utils.paper_storage import save_papers

from src.document_processing.pdf_downloader import download_pdf

from src.document_processing.pdf_extractor import (
    extract_pdf_text,
    save_extracted_text
)

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def main():

    print("=" * 60)
    print("       AUTONOMOUS AI RESEARCH AGENT")
    print("=" * 60)

    query = input("\nEnter your research topic: ").strip()

    if not query:
        print("Please enter a valid research topic.")
        return

    # STEP 1: Search research papers
    print("\nSTEP 1: Searching research papers...")

    papers = search_all_papers(
        query,
        max_results=5
    )

    if not papers:
        print("No research papers found.")
        return

    # STEP 2: Normalize paper information
    print("\nSTEP 2: Organizing research papers...")

    normalized_papers = [
        normalize_paper(paper)
        for paper in papers
    ]

    # STEP 3: Remove duplicate papers
    print("\nSTEP 3: Removing duplicate papers...")

    unique_papers = remove_duplicates(
        normalized_papers
    )

    print("Unique papers:", len(unique_papers))

    # STEP 4: Sort papers by date
    print("\nSTEP 4: Sorting research papers...")

    sorted_papers = sort_papers_by_date(
        unique_papers
    )

    # STEP 5: Download PDFs and extract text
    print("\nSTEP 5: Downloading research PDFs...")

    downloaded_count = 0
    extracted_count = 0

    for index, paper in enumerate(sorted_papers, start=1):

        print("\n" + "=" * 60)
        print(f"PROCESSING PAPER {index}/{len(sorted_papers)}")
        print("=" * 60)

        # Download PDF
        pdf_path = download_pdf(paper)

        if pdf_path is None:

            paper["download_status"] = "failed"
            paper["extraction_status"] = "skipped"

            continue

        downloaded_count += 1

        # Store the relative PDF path.
        paper["local_pdf_path"] = str(
            pdf_path.relative_to(PROJECT_ROOT).as_posix()
        )

        paper["download_status"] = "success"

        # Extract PDF text
        print("\nExtracting PDF text...")

        extracted_data = extract_pdf_text(pdf_path)

        if extracted_data is None:

            paper["extraction_status"] = "failed"

            continue

        if not extracted_data["full_text"].strip():

            paper["extraction_status"] = "no_text"

            continue

        # Save extracted text
        extracted_path = save_extracted_text(
            extracted_data,
            f"{paper['source']}_{paper['paper_id']}"
        )

        if extracted_path is None:

            paper["extraction_status"] = "save_failed"

            continue

        extracted_count += 1

        paper["extraction_status"] = "success"

        paper["page_count"] = extracted_data["page_count"]

        paper["extracted_text_path"] = str(
            extracted_path.relative_to(PROJECT_ROOT).as_posix()
        )

    # STEP 6: Save updated paper information
    print("\nSTEP 6: Saving research information...")

    saved = save_papers(sorted_papers)

    # STEP 7: Display final summary
    print("\n" + "=" * 60)
    print("           PHASE 4 PROCESSING SUMMARY")
    print("=" * 60)

    print("Total papers collected:", len(sorted_papers))

    print("PDFs downloaded:", downloaded_count)

    print("PDFs successfully extracted:", extracted_count)

    print(
        "PDFs not downloaded:",
        len(sorted_papers) - downloaded_count
    )

    if saved:
        print("\nResearch information saved successfully!")

    print("\nPHASE 4 COMPLETED!")


if __name__ == "__main__":
    main()
