
from src.api.arxiv_service import search_arxiv
from src.api.semantic_scholar_service import search_semantic_scholar


def search_all_papers(query, max_results=5):

    print("\nSearching research papers...")
    
    print("\nSearching arXiv...")
    arxiv_papers = search_arxiv(
        query,
        max_results
    )

    print("arXiv papers found:", len(arxiv_papers))

    print("\nSearching Semantic Scholar...")
    semantic_papers = search_semantic_scholar(
        query,
        max_results
    )

    print(
        "Semantic Scholar papers found:",
        len(semantic_papers)
    )

    all_papers = arxiv_papers + semantic_papers

    return all_papers
