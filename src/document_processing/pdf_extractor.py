
import json
import pymupdf

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXTRACTED_FOLDER = (
    PROJECT_ROOT / "data" / "processed" / "extracted_text"
)


def extract_pdf_text(pdf_path):
    """
    Extract text from every page of a PDF.
    """

    pages = []

    try:

        document = pymupdf.open(pdf_path)

        metadata = document.metadata or {}

        for page_number, page in enumerate(
            document,
            start=1
        ):

            text = page.get_text("text")

            pages.append({
                "page_number": page_number,
                "text": text.strip()
            })

        document.close()

        full_text = "\n\n".join(
            page["text"] for page in pages
        )

        result = {
            "file_name": Path(pdf_path).name,
            "page_count": len(pages),
            "metadata": metadata,
            "pages": pages,
            "full_text": full_text
        }

        print("\nPDF text extraction successful!")

        print("Pages extracted:", len(pages))

        print("Characters extracted:", len(full_text))

        if not full_text.strip():
            print(
                "Warning: No selectable text found. "
                "This PDF may require OCR."
            )

        return result

    except (pymupdf.FileDataError,pymupdf.EmptyFileError, OSError) as error:

        print("PDF extraction failed:", error)

        return None


def save_extracted_text(extracted_data, paper_id):
    """
    Save extracted PDF text into a JSON file.
    """

    if not extracted_data:
        return None

    EXTRACTED_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    # Generate a safe filename.
    import hashlib

    safe_id = hashlib.sha256(
        str(paper_id).encode("utf-8")
    ).hexdigest()[:16]

    output_path = (
        EXTRACTED_FOLDER / f"{safe_id}.json"
    )

    try:

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                extracted_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("Extracted text saved at:", output_path)

        return output_path

    except (OSError, TypeError, ValueError) as error:

        print("Error saving extracted text:", error)

        return None
