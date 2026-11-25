
import json
import re
import urllib.request
import urllib.error
from urllib.parse import quote
from difflib import SequenceMatcher
import time

CROSSREF_URL = "https://api.crossref.org/works/"
CROSSREF_SEARCH_URL = "https://api.crossref.org/works"


def extract_doi(*values):
    """
    Extract DOI from paper metadata or URLs.
    """

    for value in values:

        if not value:
            continue

        match = re.search(
            r"10\.\d{4,9}/[-._;()/:A-Z0-9]+",
            str(value),
            re.IGNORECASE
        )

        if match:
            return match.group(0).rstrip(".,;:)")

    return ""


def crossref_request(url, max_retries=3):

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AIResearchAgent/1.0 (mailto:research@example.com)"
        }
    )

    for attempt in range(max_retries):

        try:

            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.HTTPError as error:

            if error.code == 429:

                wait_time = 5 * (attempt + 1)

                print(
                    f"Crossref rate limit reached. "
                    f"Retrying in {wait_time} seconds..."
                )

                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue

            raise

    raise RuntimeError("Crossref request failed after retries.")


def get_crossref_metadata(item):
    """
    Extract useful metadata from a Crossref record.
    """

    titles = item.get("title") or []
    authors = item.get("author") or []

    year = ""

    date_parts = (
        item.get("published-print")
        or item.get("published-online")
        or item.get("created")
        or {}
    ).get("date-parts", [])

    if date_parts and date_parts[0]:
        year = date_parts[0][0]

    return {
        "doi": item.get("DOI", ""),
        "title": titles[0] if titles else "",
        "authors": [
            " ".join(
                part for part in [
                    author.get("given", ""),
                    author.get("family", "")
                ] if part
            )
            for author in authors
        ],
        "year": year,
        "publisher": item.get("publisher", ""),
        "type": item.get("type", "")
    }


def verify_doi(doi):
    """
    Verify a paper directly using its DOI.
    """

    if not doi:
        return {
            "status": "not_available",
            "message": "No DOI was provided.",
            "metadata": None
        }

    try:

        url = CROSSREF_URL + quote(doi, safe="")

        result = crossref_request(url)

        item = result.get("message", {})

        return {
            "status": "verified",
            "message": "DOI found in Crossref.",
            "metadata": get_crossref_metadata(item)
        }

    except urllib.error.HTTPError as error:

        if error.code == 404:
            return {
                "status": "not_found",
                "message": "DOI was not found in Crossref.",
                "metadata": None
            }

        return {
            "status": "api_error",
            "message": f"Crossref HTTP error: {error.code}",
            "metadata": None
        }

    except Exception as error:

        return {
            "status": "api_error",
            "message": str(error),
            "metadata": None
        }


def search_crossref_by_title(title):
    """
    Search Crossref using a paper title.
    """

    if not title or not title.strip():

        return {
            "status": "not_available",
            "message": "Paper title is missing.",
            "metadata": None,
            "title_match": False,
            "similarity": 0
        }

    try:

        params = (
            "?query.title=" + quote(title)
            + "&rows=5"
        )

        result = crossref_request(
            CROSSREF_SEARCH_URL + params
        )

        items = result.get("message", {}).get("items", [])

        if not items:

            return {
                "status": "not_found",
                "message": "No matching paper found in Crossref.",
                "metadata": None,
                "title_match": False,
                "similarity": 0
            }

        best_item = None
        best_similarity = 0

        original_title = title.lower().strip()

        for item in items:

            titles = item.get("title") or []

            if not titles:
                continue

            crossref_title = titles[0].lower().strip()

            similarity = SequenceMatcher(
                None,
                original_title,
                crossref_title
            ).ratio()

            if similarity > best_similarity:

                best_similarity = similarity
                best_item = item

        if best_item is None:

            return {
                "status": "not_found",
                "message": "Crossref returned no usable titles.",
                "metadata": None,
                "title_match": False,
                "similarity": 0
            }

        metadata = get_crossref_metadata(best_item)

        # Require a reasonably close title match.
        if best_similarity >= 0.90:

            return {
                "status": "verified",
                "message": "Paper matched using its title.",
                "metadata": metadata,
                "title_match": True,
                "similarity": round(best_similarity, 4)
            }

        return {
            "status": "needs_review",
            "message": "Crossref returned a possible match, but the title similarity is too low.",
            "metadata": metadata,
            "title_match": False,
            "similarity": round(best_similarity, 4)
        }

    except urllib.error.HTTPError as error:

        return {
            "status": "api_error",
            "message": f"Crossref HTTP error: {error.code}",
            "metadata": None,
            "title_match": False,
            "similarity": 0
        }

    except Exception as error:

        return {
            "status": "api_error",
            "message": str(error),
            "metadata": None,
            "title_match": False,
            "similarity": 0
        }


def verify_paper_metadata(paper):
    """
    Verify metadata using DOI first.
    If DOI is missing, search using the title.
    """

    title = paper.get("title", "")

    doi = extract_doi(
        paper.get("doi"),
        paper.get("paper_url"),
        paper.get("paper_id")
    )

    # CASE 1: DOI is available.
    if doi:

        result = verify_doi(doi)

        if result.get("status") == "verified":

            crossref_title = (
                result.get("metadata") or {}
            ).get("title", "")

            similarity = SequenceMatcher(
                None,
                title.lower().strip(),
                crossref_title.lower().strip()
            ).ratio() if title and crossref_title else 0

            result["title_match"] = similarity >= 0.90
            result["similarity"] = round(similarity, 4)

        return result

    # CASE 2: DOI is missing. Search by title.
    print(f"DOI missing. Searching Crossref by title: {title}")

    return search_crossref_by_title(title)
