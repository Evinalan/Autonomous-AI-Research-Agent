
from src.api.arxiv_service import search_arxiv
from src.api.semantic_scholar_service import search_semantic_scholar
from src.api.openalex_service import search_openalex


def search_all_papers(query, max_results=5):

    print("\nSearching research papers...")

    # STEP 1: Search arXiv
    print("\nSearching arXiv...")

    arxiv_papers = search_arxiv(
        query,
        max_results
    )

    print("arXiv papers found:", len(arxiv_papers))

    # STEP 2: Search Semantic Scholar
    print("\nSearching Semantic Scholar...")

    semantic_papers = search_semantic_scholar(
        query,
        max_results
    )

    print(
        "Semantic Scholar papers found:",
        len(semantic_papers)
    )

    # STEP 3: Search OpenAlex
    print("\nSearching OpenAlex...")

    openalex_papers = search_openalex(
        query,
        max_results
    )

    print(
        "OpenAlex papers found:",
        len(openalex_papers)
    )

    # STEP 4: Combine results
    all_papers = (
        arxiv_papers
        + semantic_papers
        + openalex_papers
    )

    print(
        "\nTotal papers collected:",
        len(all_papers)
    )

    return all_papers
