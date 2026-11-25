
def build_source_registry(chunks):

    """
    Group retrieved chunks by research paper.

    Each source keeps the original SOURCE number
    used in the RAG context.
    """

    registry = {}

    for index, chunk in enumerate(chunks, start=1):

        paper_id = chunk.get("paper_id")

        if not paper_id:
            paper_id = (
                chunk.get("source_file")
                or chunk.get("title", "Unknown") + "_"
                + str(chunk.get("source", "Unknown"))
            )

        if paper_id not in registry:

            registry[paper_id] = {
                "title": chunk.get("title", "Unknown title"),
                "authors": chunk.get("authors", []),
                "published": chunk.get("published", ""),
                "source": chunk.get("source", "Unknown"),
                "paper_id": chunk.get("paper_id", ""),
                "doi": chunk.get("doi", ""),
                "paper_url": chunk.get("paper_url", ""),
                "pages": [],
                "source_numbers": []
            }

        registry[paper_id]["source_numbers"].append(index)

        page = chunk.get("page_number")

        if page is not None:
            if page not in registry[paper_id]["pages"]:
                registry[paper_id]["pages"].append(page)

    return list(registry.values())


def display_source_registry(sources):

    print("\n" + "=" * 65)
    print("              SOURCE REGISTRY")
    print("=" * 65)

    if not sources:
        print("No research sources found.")
        return

    for source in sources:

        source_numbers = ", ".join(
            str(number)
            for number in source["source_numbers"]
        )

        print(f"\n[SOURCE {source_numbers}]")
        print("Title:", source["title"])
        print("Authors:", source["authors"])
        print("Publication year:", source["published"])
        print("Database:", source["source"])
        print("Paper ID:", source["paper_id"])
        print("DOI:", source["doi"] or "Not available")
        print("Paper URL:", source["paper_url"] or "Not available")
        print("Pages:", source["pages"])
