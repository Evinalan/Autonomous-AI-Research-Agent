
import re
from datetime import datetime


def clean_text(text):
    """
    Remove unnecessary spaces and line breaks.
    """

    if not text:
        return ""

    text = re.sub(r"\s+", " ", str(text))

    return text.strip()


def normalize_paper(paper):
    """
    Convert paper information into a common format.
    """

    title = clean_text(paper.get("title"))
    abstract = clean_text(paper.get("abstract"))

    authors = paper.get("authors") or []

    if not isinstance(authors, list):
        authors = [str(authors)]

    authors = [
        clean_text(author)
        for author in authors
        if clean_text(author)
    ]

    published = paper.get("published")

    if published:
        published = str(published)[:10]
    else:
        published = ""

    year = None

    if published:
        try:
            year = int(published[:4])
        except ValueError:
            year = None

    citation_count = paper.get("citation_count")

    if citation_count is not None:
        try:
            citation_count = int(citation_count)
        except (ValueError, TypeError):
            citation_count = None

    # Preserve the original paper ID
    original_id = paper.get("paper_id") or ""

    paper_id = original_id

    pdf_url = paper.get("pdf_url") or ""
    paper_url = paper.get("paper_url") or ""

    if original_id.startswith("http"):
        paper_url = paper_url or original_id

        # Convert arXiv URL into a shorter paper ID
        if paper_id.startswith("http://arxiv.org/abs/"):
            paper_id = paper_id.replace(
                "http://arxiv.org/abs/",
                ""
            )

        elif paper_id.startswith("https://arxiv.org/abs/"):
            paper_id = paper_id.replace(
                "https://arxiv.org/abs/",
                ""
            )

    # Generate an ID if the API does not provide one
    if not paper_id:
        paper_id = title.lower()

    return {
        "paper_id": paper_id,
        "source": paper.get("source") or "unknown",
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "published": published,
        "year": year,
        "pdf_url": pdf_url,
        "paper_url": paper_url,
        "citation_count": citation_count
    }


def get_title_key(title):
    """
    Create a normalized title for duplicate detection.
    """

    title = clean_text(title).lower()

    title = re.sub(r"[^\w\s]", "", title)

    return title


def remove_duplicates(papers):
    """
    Remove duplicate research papers using their titles.
    """

    unique_papers = {}

    for paper in papers:

        title_key = get_title_key(
            paper.get("title", "")
        )

        if not title_key:
            continue

        if title_key not in unique_papers:
            unique_papers[title_key] = paper

        else:
            existing = unique_papers[title_key]

            # Preserve useful information from duplicates
            if not existing.get("abstract") and paper.get("abstract"):
                existing["abstract"] = paper["abstract"]

            if not existing.get("pdf_url") and paper.get("pdf_url"):
                existing["pdf_url"] = paper["pdf_url"]

            if not existing.get("paper_url") and paper.get("paper_url"):
                existing["paper_url"] = paper["paper_url"]

            if not existing.get("authors") and paper.get("authors"):
                existing["authors"] = paper["authors"]

            if existing.get("citation_count") is None:
                existing["citation_count"] = paper.get(
                    "citation_count"
                )

    return list(unique_papers.values())


def sort_papers_by_date(papers):
    """
    Sort papers from newest to oldest.
    """

    def get_date(paper):
        published = paper.get("published", "")

        try:
            return datetime.strptime(
                published[:10],
                "%Y-%m-%d"
            )
        except (ValueError, TypeError):
            return datetime.min

    return sorted(
        papers,
        key=get_date,
        reverse=True
    )
