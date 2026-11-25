
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from src.api.request_utils import get_with_retries

ARXIV_API_URL = "https://export.arxiv.org/api/query"

NAMESPACE = {
    "atom": "http://www.w3.org/2005/Atom"
}


def search_arxiv(query, max_results=5):

    try:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }

        response = get_with_retries(
                   ARXIV_API_URL,
                   params,
                   timeout=30
        )

        if response is None:
               return []
        root = ET.fromstring(response.content)

        papers = []

        for entry in root.findall("atom:entry", NAMESPACE):

            title = entry.findtext(
                "atom:title", default="", namespaces=NAMESPACE
            ).strip()

            abstract = entry.findtext(
                "atom:summary", default="", namespaces=NAMESPACE
            ).strip()

            published = entry.findtext(
                "atom:published", default="", namespaces=NAMESPACE
            )

            paper_id = entry.findtext(
                "atom:id", default="", namespaces=NAMESPACE
            )

            authors = [
                author.findtext(
                    "atom:name", default="", namespaces=NAMESPACE
                )
                for author in entry.findall("atom:author", NAMESPACE)
            ]

            pdf_url = ""

            for link in entry.findall("atom:link", NAMESPACE):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href", "")

            papers.append({
                "source": "arxiv",
                "paper_id": paper_id,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "published": published,
                "pdf_url": pdf_url
            })

        return papers

    except requests.exceptions.RequestException as error:
        print("arXiv API request failed:", error)

    except ET.ParseError as error:
        print("Could not parse arXiv response:", error)

    return []
