from hashlib import sha256
from typing import Protocol


class EmbeddingProvider(Protocol):
    provider_id: str

    def embed_query(self, text: str) -> list[float]:
        ...

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...


class LocalHashEmbeddings:
    """Deterministic local embeddings so ingest/retrieval work without a paid API."""

    provider_id = "local_hash"

    def __init__(self, dimensions: int = 32):
        self.dimensions = dimensions

    def embed_query(self, text: str) -> list[float]:
        digest = sha256(text.lower().encode("utf-8")).digest()
        values = [digest[i % len(digest)] / 255.0 for i in range(self.dimensions)]
        return values

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]


def embedding_id_for(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()[:24]


def get_embedding_provider() -> EmbeddingProvider:
    from app.core.config import get_settings

    settings = get_settings()
    if settings.embedding_api_key:
        try:
            from ai.rag.remote_embeddings import RemoteEmbeddings

            return RemoteEmbeddings()
        except Exception:
            return LocalHashEmbeddings()
    return LocalHashEmbeddings()
