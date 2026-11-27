
import os
import requests

from src.api.request_utils import get_with_retries


OPENALEX_API_URL = "https://api.openalex.org/works"


def reconstruct_abstract(inverted_index):
    """
    Convert OpenAlex's inverted-index abstract
    into normal readable text.
    """

    if not inverted_index:
        return ""

    words = {}

    for word, positions in inverted_index.items():

        for position in positions:
            words[position] = word

    if not words:
        return ""

    abstract = " ".join(
        words[position]
        for position in sorted(words)
    )

    return abstract


def search_openalex(query, max_results=5):
    """
    Search OpenAlex for research papers.

    Returns papers in the same format used by
    the arXiv and Semantic Scholar services.
    """

    if not query or not query.strip():
        return []

    try:

        params = {
    "search": query.strip(),

    # Retrieve scholarly articles, conference papers,
    # preprints and review articles.
    "filter": (
        "type:article|conference-paper|preprint|review"
    ),

    "per_page": max_results,

    "select": (
        "id,doi,title,publication_date,"
        "authorships,abstract_inverted_index,"
        "best_oa_location,primary_location,"
        "open_access,cited_by_count,type"
    )
}

        # Add the API key only if one is configured.
        api_key = os.getenv("OPENALEX_API_KEY")

        if api_key:
            params["api_key"] = api_key

        print("\nSearching OpenAlex...")

        response = get_with_retries(
            OPENALEX_API_URL,
            params,
            timeout=45
        )

        if response is None:
            print("OpenAlex did not return a response.")
            return []

        data = response.json()

        papers = []

        for work in data.get("results", []):

            title = work.get("title") or ""

            if not title.strip():
                continue

            # Reconstruct the abstract.
            abstract = reconstruct_abstract(
                work.get("abstract_inverted_index")
            )

            # Extract author names.
            authors = []

            for authorship in work.get("authorships", []):

                author = authorship.get("author") or {}

                author_name = author.get("display_name")

                if author_name:
                    authors.append(author_name)

            # Find an open-access PDF URL.
            best_location = (
                work.get("best_oa_location") or {}
            )

            primary_location = (
                work.get("primary_location") or {}
            )

            pdf_url = (
                best_location.get("pdf_url")
                or primary_location.get("pdf_url")
                or ""
            )

            # Extract publication date.
            published = work.get("publication_date") or ""

            # Use DOI when available; otherwise use OpenAlex URL.
            doi = work.get("doi") or ""

            paper_url = (
                doi
                or work.get("id")
                or ""
            )

            papers.append({
                "source": "openalex",
                "paper_id": work.get("id"),
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "published": published,
                "pdf_url": pdf_url,
                "paper_url": paper_url,
                "citation_count": work.get(
                    "cited_by_count", 0
                ),
                "publication_type": work.get("type", "")
            })

        print("OpenAlex papers found:", len(papers))

        return papers

    except requests.exceptions.RequestException as error:

        print("OpenAlex API request failed:", error)

    except (ValueError, TypeError, AttributeError) as error:

        print("Could not process OpenAlex response:", error)

    return []
