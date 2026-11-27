
from src.api.paper_search import search_all_papers

from src.utils.paper_utils import (
    normalize_paper,
    remove_duplicates,
    sort_papers_by_date,
    rank_papers_by_relevance
)

from src.utils.paper_storage import save_papers

from src.document_processing.pdf_downloader import download_pdf

from src.document_processing.pdf_extractor import (
    extract_pdf_text,
    save_extracted_text
)

from src.text_processing.text_chunker import split_text_into_chunks

from src.rag.embedding_generator import generate_embeddings

from src.rag.vector_store import create_vector_store


def prepare_research_database(topic, max_papers=5):

    """
    Search for papers related to the research topic.

    Download available PDFs, extract their text,
    create chunks, generate embeddings and build
    a topic-specific FAISS index in memory.
    """

    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    topic = topic.strip()

    print("\n========== PAPER COLLECTION ==========")

    # STEP 1: Search research databases

    print("\nSTEP 1: Searching research databases...")

    raw_papers = search_all_papers(
        topic,
        max_results=max_papers
    )

    if not raw_papers:
        raise RuntimeError(
            "No research papers were found for this topic."
        )

    print("Total papers retrieved:", len(raw_papers))

    # STEP 2: Normalize paper information

    print("\nSTEP 2: Normalizing paper information...")

    papers = [
        normalize_paper(paper)
        for paper in raw_papers
    ]

    # STEP 3: Remove duplicate papers
    print("\nSTEP 3: Removing duplicate papers...")

    papers = remove_duplicates(papers)

    print("Unique papers:", len(papers))


    print("\nSTEP 4: Ranking papers by relevance...")

    papers = rank_papers_by_relevance(
    papers,
    topic
    )

    for paper in papers[:5]:

     print(
        "Relevance:",
        paper.get("relevance_score", 0),
        "| Title:",
        paper.get("title")
     )


    print("\nSTEP 5: Sorting papers by publication date...")

    papers = sort_papers_by_date(papers)
    # Save paper metadata

    save_papers(papers)

    # STEP 4: Download PDFs and extract text

    print("\nSTEP 4: Downloading and extracting PDFs...")

    all_chunks = []

    successfully_processed = 0

    for paper_number, paper in enumerate(papers, start=1):

        print(
            f"\nProcessing paper {paper_number}/{len(papers)}"
        )

        print("Title:", paper.get("title"))

        # Download PDF

        pdf_path = download_pdf(paper)

        if not pdf_path:
            print("Skipping paper: PDF could not be downloaded.")
            continue

        # Extract PDF text

        extracted_data = extract_pdf_text(pdf_path)

        if not extracted_data:
            print("Skipping paper: Text extraction failed.")
            continue

        full_text = extracted_data.get("full_text", "")

        if not full_text.strip():
            print("Skipping paper: No extractable text.")
            continue

        # Save extracted text

        save_extracted_text(
            extracted_data,
            paper.get("paper_id") or paper.get("title")
        )

        # STEP 5: Split each page into chunks

        for page in extracted_data.get("pages", []):

            page_text = page.get("text", "").strip()

            if not page_text:
                continue

            page_chunks = split_text_into_chunks(page_text)

            for chunk_text in page_chunks:

                all_chunks.append({
                    "paper_id": paper.get("paper_id"),
                    "title": paper.get("title"),
                    "authors": paper.get("authors", []),
                    "source": paper.get("source"),
                    "published": paper.get("published"),
                    "paper_url": paper.get("paper_url"),
                    "pdf_url": paper.get("pdf_url"),
                    "page_number": page.get("page_number"),
                    "text": chunk_text
                })

        successfully_processed += 1

    print("\nSuccessfully processed papers:", successfully_processed)

    print("Total text chunks:", len(all_chunks))

    if not all_chunks:
        raise RuntimeError(
            "No text chunks were generated. "
            "The papers may not have downloadable or extractable PDFs."
        )

    # STEP 6: Generate embeddings

    print("\nSTEP 6: Generating embeddings...")

    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    embeddings = generate_embeddings(texts)

    print("Total embeddings generated:", len(embeddings))

    # STEP 7: Build an in-memory FAISS index

    print("\nSTEP 7: Building topic-specific FAISS index...")

    vector_index = create_vector_store(
        all_chunks,
        embeddings
    )

    print("\n========== DATABASE READY ==========")

    return {
        "topic": topic,
        "papers": papers,
        "processed_papers": successfully_processed,
        "chunks": all_chunks,
        "vector_index": vector_index
    }
