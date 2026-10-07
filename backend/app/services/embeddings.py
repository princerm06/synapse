from functools import lru_cache
from typing import Any


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model() -> Any:
    """Load the embedding model only when retrieval/ingestion first needs it."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    embedding = get_model().encode(text)
    return embedding.tolist()
