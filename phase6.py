
import json
from pathlib import Path

from src.rag.embedding_generator import (
    generate_embeddings,
    generate_query_embedding
)

from src.rag.vector_store import (
    create_vector_store,
    save_vector_store,
    search_similar_chunks
)


PROJECT_ROOT = Path(__file__).resolve().parent

CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "all_chunks.json"
)


def load_chunks():

    if not CHUNKS_FILE.exists():

        print("Phase 5 chunks file not found!")
        print("Expected location:", CHUNKS_FILE)

        return []

    try:

        with open(
            CHUNKS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            chunks = json.load(file)

        # Remove empty chunks
        chunks = [
            chunk
            for chunk in chunks
            if chunk.get("text", "").strip()
        ]

        return chunks

    except (OSError, json.JSONDecodeError) as error:

        print("Error loading chunks:", error)

        return []


def main():

    print("=" * 60)
    print("       PHASE 6: EMBEDDINGS & VECTOR DATABASE")
    print("=" * 60)

    # STEP 1: Load chunks
    print("\nSTEP 1: Loading research chunks...")

    chunks = load_chunks()

    if not chunks:

        print("No research chunks available.")
        print("Complete Phase 5 before running Phase 6.")

        return

    print("Total chunks loaded:", len(chunks))

    # STEP 2: Extract text
    print("\nSTEP 2: Preparing text for embeddings...")

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print("Texts prepared:", len(texts))

    # STEP 3: Generate embeddings
    print("\nSTEP 3: Generating embeddings...")

    embeddings = generate_embeddings(texts)

    print("\nEmbeddings generated successfully!")
    print("Embedding shape:", embeddings.shape)

    # STEP 4: Create FAISS index
    print("\nSTEP 4: Creating FAISS vector database...")

    index = create_vector_store(
        chunks,
        embeddings
    )

    # STEP 5: Save vector database
    print("\nSTEP 5: Saving vector database...")

    saved = save_vector_store(
        index,
        chunks
    )

    if not saved:
        print("Vector database could not be saved.")
        return

    # STEP 6: Test semantic search
    print("\nSTEP 6: Testing semantic search...")

    query = input(
        "\nEnter a research question to test: "
    ).strip()

    if not query:
        print("No test question entered. Skipping search.")
    else:

        query_embedding = generate_query_embedding(query)

        results = search_similar_chunks(
            query_embedding,
            top_k=5
        )

        print("\nMOST RELEVANT RESEARCH CHUNKS")
        print("=" * 60)

        for number, result in enumerate(results, start=1):

            print(f"\nRESULT {number}")
            print("-" * 60)

            print("Title:", result.get("title"))
            print("Page:", result.get("page_number"))
            print(
                "Similarity:",
                round(result["similarity_score"], 4)
            )

            print("\nText:")
            print(result.get("text", "")[:700])

    # SUMMARY
    print("\n" + "=" * 60)
    print("           PHASE 6 SUMMARY")
    print("=" * 60)

    print("Total chunks embedded:", len(chunks))
    print("Embedding dimensions:", embeddings.shape[1])
    print("FAISS vectors stored:", index.ntotal)

    print("\nPHASE 6 COMPLETED!")


if __name__ == "__main__":
    main()
