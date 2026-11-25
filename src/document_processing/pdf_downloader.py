
import requests
import re
import hashlib

from pathlib import Path
from urllib.parse import urlparse


# Locate the main project directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Folder where downloaded PDFs will be stored.
PDF_FOLDER = PROJECT_ROOT / "data" / "papers"

# Maximum allowed PDF size: 50 MB.
MAX_PDF_SIZE = 50 * 1024 * 1024


def create_pdf_filename(paper):
    """
    Generate a safe and unique filename for each paper.
    """

    paper_id = str(
        paper.get("paper_id") or paper.get("title") or "paper"
    )

    title = paper.get("title") or "research-paper"

    # Create a short readable filename.
    title_slug = re.sub(
        r"[^a-zA-Z0-9]+",
        "-",
        title.lower()
    ).strip("-")[:50]

    # Create a unique hash using source and paper ID.
    unique_value = (
        str(paper.get("source", "")) + paper_id
    )

    unique_hash = hashlib.sha256(
        unique_value.encode("utf-8")
    ).hexdigest()[:12]

    return f"{title_slug}-{unique_hash}.pdf"


def download_pdf(paper):
    """
    Download an individual research paper PDF.
    """

    pdf_url = paper.get("pdf_url")

    if not pdf_url:
        print("PDF URL not available:", paper.get("title"))
        return None

    # Accept only HTTP and HTTPS URLs.
    parsed_url = urlparse(pdf_url)

    if parsed_url.scheme not in ("http", "https"):
        print("Invalid PDF URL:", pdf_url)
        return None

    PDF_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = create_pdf_filename(paper)

    pdf_path = PDF_FOLDER / filename

    # Avoid downloading the same file repeatedly.
    if pdf_path.exists() and pdf_path.stat().st_size > 0:
        with open(pdf_path, "rb") as file:
            if file.read(5) == b"%PDF-":
                print("PDF already downloaded:", filename)
                return pdf_path

        pdf_path.unlink()

    temp_path = pdf_path.with_suffix(".part")

    try:

        print("\nDownloading:", paper.get("title"))

        headers = {
            "User-Agent": "AI-Research-Agent/1.0"
        }

        response = requests.get(
            pdf_url,
            headers=headers,
            stream=True,
            timeout=(15, 60)
        )

        response.raise_for_status()

        content_length = response.headers.get(
            "Content-Length"
        )

        if content_length:
            if int(content_length) > MAX_PDF_SIZE:
                print("PDF exceeds the 50 MB size limit.")
                return None

        total_size = 0

        with open(temp_path, "wb") as file:

            for chunk in response.iter_content(
                chunk_size=8192
            ):

                if not chunk:
                    continue

                total_size += len(chunk)

                if total_size > MAX_PDF_SIZE:
                    raise ValueError(
                        "PDF exceeds the 50 MB size limit."
                    )

                file.write(chunk)

        # Verify that the downloaded file is actually a PDF.
        with open(temp_path, "rb") as file:
            file_header = file.read(5)

        if file_header != b"%PDF-":
            raise ValueError(
                "Downloaded file is not a valid PDF."
            )

        # Rename temporary file after successful validation.
        temp_path.replace(pdf_path)

        print("PDF downloaded successfully!")
        print("Saved at:", pdf_path)

        return pdf_path

    except (
        requests.exceptions.RequestException,
        OSError,
        ValueError
    ) as error:

        print("PDF download failed:", error)

        return None

    finally:

        response.close() if "response" in locals() else None

        if temp_path.exists():
            temp_path.unlink()
