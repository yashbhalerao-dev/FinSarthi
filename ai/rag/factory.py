from sqlmodel import Session

from ai.rag.local_retriever import LocalMetadataRetriever
from ai.rag.retriever import RetrievedChunk, Retriever
from app.core.config import get_settings


class FallbackRetriever:
    """Pinecone first when configured; always falls back to the local corpus retriever."""

    def __init__(self, session: Session):
        self.local = LocalMetadataRetriever(session)
        self.remote: Retriever | None = None
        if get_settings().pinecone_enabled:
            try:
                from ai.rag.pinecone_retriever import PineconeRetriever

                self.remote = PineconeRetriever()
            except Exception:
                self.remote = None

    def retrieve(
        self,
        query: str,
        *,
        jurisdiction: str | None = None,
        applicant_type: str | None = None,
        limit: int = 8,
    ) -> list[RetrievedChunk]:
        if self.remote is not None:
            remote_hits = self.remote.retrieve(
                query,
                jurisdiction=jurisdiction,
                applicant_type=applicant_type,
                limit=limit,
            )
            if remote_hits:
                return remote_hits
        return self.local.retrieve(
            query,
            jurisdiction=jurisdiction,
            applicant_type=applicant_type,
            limit=limit,
        )


def get_retriever(session: Session) -> FallbackRetriever:
    return FallbackRetriever(session)


def as_langchain_retriever(session: Session):
    retriever = get_retriever(session)
    try:
        from langchain_core.documents import Document
        from langchain_core.retrievers import BaseRetriever
        from typing import Any

        class FinSarthiLangChainRetriever(BaseRetriever):
            k: int = 8

            def _get_relevant_documents(self, query: str, *, run_manager: Any = None) -> list:
                hits = retriever.retrieve(query, limit=self.k)
                return [
                    Document(
                        page_content=hit.text,
                        metadata={
                            "policy_id": hit.policy_id,
                            "chunk_id": hit.id,
                            "section": hit.section,
                            "page_reference": hit.page_reference,
                            "source_url": hit.source_url,
                            **(hit.metadata or {}),
                        },
                    )
                    for hit in hits
                ]

        return FinSarthiLangChainRetriever()
    except Exception:
        from ai.rag.langchain_bridge import to_langchain_documents

        class _Shim:
            def invoke(self, query: str):
                return to_langchain_documents(retriever.retrieve(query))

        return _Shim()
