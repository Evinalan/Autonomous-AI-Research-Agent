
import requests

from src.api.request_utils import get_with_retries
SEMANTIC_SCHOLAR_URL = (
    "https://api.semanticscholar.org/graph/v1/paper/search"
)


def search_semantic_scholar(query, limit=5):

    try:
        params = {
            "query": query,
            "limit": limit,
            "fields": (
                "title,abstract,authors,year,url,"
                "openAccessPdf,citationCount,publicationDate"
            )
        }

        response = get_with_retries(
                   SEMANTIC_SCHOLAR_URL,
                   params,
                   timeout=30
        )

        if response is None:
             return []
        data = response.json()

        papers = []

        for paper in data.get("data", []):

            open_access = paper.get("openAccessPdf") or {}

            authors = [
                author.get("name", "")
                for author in paper.get("authors", [])
            ]

            papers.append({
                "source": "semantic_scholar",
                "paper_id": paper.get("paperId"),
                "title": paper.get("title"),
                "abstract": paper.get("abstract"),
                "authors": authors,
                "published": paper.get("publicationDate") or paper.get("year"),
                "pdf_url": open_access.get("url", ""),
                "citation_count": paper.get("citationCount", 0),
                "paper_url": paper.get("url", "")
            })

        return papers

    except requests.exceptions.RequestException as error:
        print("Semantic Scholar API request failed:", error)

    except ValueError as error:
        print("Could not decode Semantic Scholar response:", error)

    return []
