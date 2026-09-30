"""Pinecone retriever. Live calls run only when PINECONE_API_KEY and PINECONE_INDEX are set."""

from app.core.config import get_settings
from ai.rag.retriever import RetrievedChunk


class PineconeRetriever:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.pinecone_enabled:
            raise RuntimeError("Pinecone is not configured")
        self.api_key = settings.pinecone_api_key
        self.index_name = settings.pinecone_index
        self.environment = settings.pinecone_environment
        self._client = None
        try:
            from pinecone import Pinecone  # type: ignore

            self._client = Pinecone(api_key=self.api_key)
        except Exception:
            self._client = None

    def retrieve(
        self,
        query: str,
        *,
        jurisdiction: str | None = None,
        applicant_type: str | None = None,
        limit: int = 8,
    ) -> list[RetrievedChunk]:
        if self._client is None:
            return []
        try:
            from ai.rag.embeddings import get_embedding_provider

            vector = get_embedding_provider().embed_query(query)
            index = self._client.Index(self.index_name)
            filters: dict[str, str] = {}
            if jurisdiction:
                filters["jurisdiction"] = jurisdiction
            if applicant_type:
                filters["applicant_type"] = applicant_type
            response = index.query(
                vector=vector,
                top_k=limit,
                include_metadata=True,
                filter=filters or None,
            )
            matches = getattr(response, "matches", None) or response.get("matches", [])
            chunks: list[RetrievedChunk] = []
            for match in matches:
                meta = getattr(match, "metadata", None) or match.get("metadata") or {}
                chunks.append(
                    RetrievedChunk(
                        id=str(meta.get("chunk_id") or getattr(match, "id", "")),
                        policy_id=str(meta.get("policy_id") or ""),
                        text=str(meta.get("text") or ""),
                        section=meta.get("section"),
                        page_reference=meta.get("page_reference"),
                        source_url=meta.get("source_url"),
                        metadata=dict(meta),
                        score=float(getattr(match, "score", 0) or match.get("score") or 0),
                        embedding_id=str(getattr(match, "id", "")),
                    )
                )
            return chunks
        except Exception:
            return []
