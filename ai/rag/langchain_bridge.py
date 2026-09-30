from ai.rag.retriever import RetrievedChunk

try:
    from langchain_core.documents import Document as LCDocument
except ImportError:  # LangChain is optional at runtime until retrieval phase wiring
    LCDocument = None


def to_langchain_documents(chunks: list[RetrievedChunk]):
    if LCDocument is None:
        return [
            {
                "page_content": chunk.text,
                "metadata": {
                    "policy_id": chunk.policy_id,
                    "chunk_id": chunk.id,
                    "section": chunk.section,
                    "page_reference": chunk.page_reference,
                    "source_url": chunk.source_url,
                    **(chunk.metadata or {}),
                },
            }
            for chunk in chunks
        ]
    return [
        LCDocument(
            page_content=chunk.text,
            metadata={
                "policy_id": chunk.policy_id,
                "chunk_id": chunk.id,
                "section": chunk.section,
                "page_reference": chunk.page_reference,
                **(chunk.metadata or {}),
            },
        )
        for chunk in chunks
    ]
