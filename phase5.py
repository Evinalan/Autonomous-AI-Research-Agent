
import json
from pathlib import Path

from src.text_processing.text_cleaner import clean_text
from src.text_processing.text_chunker import split_text_into_chunks


PROJECT_ROOT = Path(__file__).resolve().parent

EXTRACTED_FOLDER = (
    PROJECT_ROOT / "data" / "processed" / "extracted_text"
)

PAPER_FILE = (
    PROJECT_ROOT / "data" / "processed" / "research_papers.json"
)

CHUNKS_FOLDER = (
    PROJECT_ROOT / "data" / "processed" / "chunks"
)


def load_paper_metadata():

    if not PAPER_FILE.exists():
        print("Research paper metadata file not found.")
        return {}

    try:
        with open(PAPER_FILE, "r", encoding="utf-8") as file:
            papers = json.load(file)

        metadata_lookup = {}

        for paper in papers:

            extracted_path = paper.get("extracted_text_path")

            if extracted_path:
                normalized_path = extracted_path.replace("\\", "/")
                metadata_lookup[normalized_path] = paper

        return metadata_lookup

    except (OSError, json.JSONDecodeError) as error:
        print("Could not load paper metadata:", error)
        return {}


def process_paper(extracted_file, metadata_lookup):

    try:
        with open(extracted_file, "r", encoding="utf-8") as file:
            extracted_data = json.load(file)

    except (OSError, json.JSONDecodeError) as error:
        print("Could not read:", extracted_file.name, error)
        return []

    relative_path = extracted_file.relative_to(
        PROJECT_ROOT
    ).as_posix()

    paper = metadata_lookup.get(relative_path, {})

    paper_id = paper.get("paper_id") or extracted_file.stem
    title = paper.get("title") or extracted_data.get("file_name", "")
    authors = paper.get("authors") or []
    source = paper.get("source") or "unknown"
    published = paper.get("published") or ""

    pages = extracted_data.get("pages", [])

    # Fallback for files that contain full_text but no pages list
    if not pages and extracted_data.get("full_text"):
        pages = [{
            "page_number": 1,
            "text": extracted_data["full_text"]
        }]

    paper_chunks = []
    chunk_number = 0

    for page in pages:

        page_number = page.get("page_number", 1)
        original_text = page.get("text", "")

        cleaned_text = clean_text(original_text)

        if not cleaned_text:
            continue

        text_chunks = split_text_into_chunks(cleaned_text)

        for chunk_text in text_chunks:

            chunk_number += 1

            chunk = {
                "chunk_id": (
                    f"{extracted_file.stem}_chunk_{chunk_number}"
                ),
                "paper_id": paper_id,
                "title": title,
                "authors": authors,
                "source": source,
                "published": published,
                "page_number": page_number,
                "chunk_number": chunk_number,
                "text": chunk_text,
                "source_file": relative_path,
                "doi": paper.get("doi", ""),
                "paper_url": paper.get("paper_url", ""),
                "pdf_url": paper.get("pdf_url", "")
            }

            paper_chunks.append(chunk)

    return paper_chunks


def save_chunks(chunks, output_path):

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(
                chunks,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except (OSError, TypeError, ValueError) as error:
        print("Could not save chunks:", error)
        return False


def main():

    print("=" * 60)
    print("       PHASE 5: TEXT PREPROCESSING & CHUNKING")
    print("=" * 60)

    if not EXTRACTED_FOLDER.exists():
        print("Extracted text folder not found:", EXTRACTED_FOLDER)
        return

    extracted_files = list(EXTRACTED_FOLDER.glob("*.json"))

    if not extracted_files:
        print("No extracted JSON files found.")
        print("Complete Phase 4 before running Phase 5.")
        return

    metadata_lookup = load_paper_metadata()

    all_chunks = []
    processed_papers = 0

    for index, extracted_file in enumerate(extracted_files, start=1):

        print("\n" + "=" * 60)
        print(f"PROCESSING PAPER {index}/{len(extracted_files)}")
        print("=" * 60)

        print("File:", extracted_file.name)

        chunks = process_paper(
            extracted_file,
            metadata_lookup
        )

        if not chunks:
            print("No usable text chunks were created.")
            continue

        output_file = (
            CHUNKS_FOLDER /
            f"chunks_{extracted_file.stem}.json"
        )

        if save_chunks(chunks, output_file):

            all_chunks.extend(chunks)
            processed_papers += 1

            print("Chunks created:", len(chunks))
            print("Saved at:", output_file)

    # Save all chunks together for the next phase
    combined_output = CHUNKS_FOLDER / "all_chunks.json"

    combined_saved = save_chunks(
        all_chunks,
        combined_output
    )

    print("\n" + "=" * 60)
    print("           PHASE 5 SUMMARY")
    print("=" * 60)

    print("Extracted files found:", len(extracted_files))
    print("Papers processed:", processed_papers)
    print("Total chunks created:", len(all_chunks))

    if combined_saved:
        print("Combined chunks saved at:", combined_output)

    print("\nPHASE 5 PROCESSING COMPLETED!")


if __name__ == "__main__":
    main()
