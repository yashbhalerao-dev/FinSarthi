"""Optional remote embeddings. Local hash embeddings are the default."""

from app.core.config import get_settings


class RemoteEmbeddings:
    provider_id = "remote"

    def embed_query(self, text: str) -> list[float]:
        del text
        raise RuntimeError("Remote embeddings require a configured embedding API.")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        del texts
        raise RuntimeError("Remote embeddings require a configured embedding API.")
