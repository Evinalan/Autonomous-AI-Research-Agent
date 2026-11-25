
from functools import lru_cache
from sentence_transformers import SentenceTransformer

# Free, locally running embedding model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load the embedding model once and reuse it.
    """

    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Embedding model loaded successfully!")

    return model


def generate_embeddings(texts):
    """
    Convert a list of text chunks into numerical embeddings.
    """

    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings


def generate_query_embedding(query):
    """
    Convert a user's question into an embedding.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    model = get_embedding_model()

    embedding = model.encode(
        [query],
        batch_size=1,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embedding
