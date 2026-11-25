
import json
import faiss
import numpy as np

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

VECTOR_FOLDER = (
    PROJECT_ROOT / "data" / "processed" / "vector_store"
)

INDEX_PATH = VECTOR_FOLDER / "research.index"

METADATA_PATH = VECTOR_FOLDER / "chunks_metadata.json"


def create_vector_store(chunks, embeddings):
    """
    Create a FAISS vector index from text embeddings.
    """

    if len(chunks) == 0:
        raise ValueError("No chunks were provided.")

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D array.")

    if embeddings.shape[0] != len(chunks):
        raise ValueError(
            "Number of embeddings must match number of chunks."
        )

    if embeddings.shape[1] == 0:
        raise ValueError("Embedding dimension cannot be zero.")

    if not np.isfinite(embeddings).all():
        raise ValueError("Embeddings contain invalid values.")

    # Create an index using inner product.
    # Because our vectors are normalized, this is cosine similarity.
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    print("\nFAISS vector index created successfully!")
    print("Total vectors:", index.ntotal)
    print("Vector dimensions:", dimension)

    return index


def save_vector_store(index, chunks):
    """
    Save the FAISS index and corresponding chunk metadata.
    """

    try:
        VECTOR_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )

        # Save the FAISS index
        faiss.write_index(
            index,
            str(INDEX_PATH)
        )

        # Save metadata in exactly the same order as vectors
        with open(
            METADATA_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                chunks,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\nVector database saved successfully!")
        print("Index:", INDEX_PATH)
        print("Metadata:", METADATA_PATH)

        return True

    except (OSError, TypeError, ValueError) as error:

        print("Error saving vector database:", error)

        return False


def load_vector_store():
    """
    Load an existing FAISS index and its metadata.
    """

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            "FAISS index not found. Run phase6.py first."
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Chunk metadata not found. Run phase6.py first."
        )

    index = faiss.read_index(str(INDEX_PATH))

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    if index.ntotal != len(chunks):
        raise ValueError(
            "FAISS index and metadata have different sizes."
        )

    return index, chunks


def search_similar_chunks(query_embedding, top_k=5):
    """
    Find the most similar research chunks for a query embedding.
    """

    index, chunks = load_vector_store()

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    if query_embedding.shape[1] != index.d:
        raise ValueError(
            "Query embedding dimension does not match FAISS index."
        )

    if not np.isfinite(query_embedding).all():
        raise ValueError("Query embedding contains invalid values.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    if index.ntotal == 0:
        return []

    top_k = min(top_k, index.ntotal)

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, chunk_index in zip(
        scores[0],
        indices[0]
    ):

        if chunk_index < 0:
            continue

        result = chunks[int(chunk_index)].copy()

        result["similarity_score"] = float(score)

        results.append(result)

    return results
