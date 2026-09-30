from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class RetrievedChunk:
    id: str
    policy_id: str
    text: str
    section: str | None
    page_reference: str | None
    source_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    embedding_id: str | None = None


class Retriever(Protocol):
    def retrieve(
        self,
        query: str,
        *,
        jurisdiction: str | None = None,
        applicant_type: str | None = None,
        limit: int = 8,
    ) -> list[RetrievedChunk]:
        ...
