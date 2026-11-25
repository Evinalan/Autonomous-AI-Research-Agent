
def run_citation_agent(chunks):

    sources = {}

    for index, chunk in enumerate(chunks, start=1):

        paper_id = chunk.get("paper_id")

        if not paper_id:
            paper_id = chunk.get("source_file") or (
                chunk.get("title", "Unknown") + "_" +
                str(chunk.get("source", "Unknown"))
            )

        if paper_id not in sources:

            sources[paper_id] = {
                "title": chunk.get("title", "Unknown title"),
                "authors": chunk.get("authors", []),
                "published": chunk.get("published", ""),
                "source": chunk.get("source", "Unknown"),
                "paper_id": chunk.get("paper_id", ""),
                "pages": [],
                "source_numbers": []
            }

        sources[paper_id]["source_numbers"].append(index)

        page = chunk.get("page_number")

        if page is not None and page not in sources[paper_id]["pages"]:
            sources[paper_id]["pages"].append(page)

    return list(sources.values())


def display_citations(sources):

    print("\n" + "=" * 60)
    print("RESEARCH PAPER REFERENCES")
    print("=" * 60)

    if not sources:
        print("No source metadata available.")
        return

    for source in sources:

        numbers = ", ".join(
            str(number)
            for number in source["source_numbers"]
        )

        print(f"\n[SOURCE {numbers}]")
        print("Title:", source["title"])
        print("Authors:", source["authors"])
        print("Publication year:", source["published"])
        print("Database:", source["source"])
        print("Paper ID:", source["paper_id"])
        print("Pages:", source["pages"])
