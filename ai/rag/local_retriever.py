from sqlmodel import Session, select

from ai.rag.retriever import RetrievedChunk
from app.models.entities import Policy, PolicyChunk


class LocalMetadataRetriever:
    """Keyword + metadata retrieval used when Pinecone is not configured."""

    def __init__(self, session: Session):
        self.session = session

    def retrieve(
        self,
        query: str,
        *,
        jurisdiction: str | None = None,
        applicant_type: str | None = None,
        limit: int = 8,
    ) -> list[RetrievedChunk]:
        policies = list(self.session.exec(select(Policy)).all())
        by_id = {policy.id: policy for policy in policies}
        chunks = list(self.session.exec(select(PolicyChunk)).all())
        tokens = {part.lower() for part in query.split() if len(part) > 2}
        scored: list[RetrievedChunk] = []
        for chunk in chunks:
            policy = by_id.get(chunk.policy_id)
            if policy is None:
                continue
            if applicant_type and policy.applicant_type not in {applicant_type, "any"}:
                continue
            text = f"{policy.name} {policy.category} {chunk.text}".lower()
            overlap = len(tokens.intersection(text.split())) if tokens else 1
            jurisdiction_bonus = 2 if jurisdiction and policy.jurisdiction.lower() == jurisdiction.lower() else 0
            if jurisdiction and policy.jurisdiction.lower() != jurisdiction.lower():
                overlap = max(overlap - 3, 0)
            score = overlap + jurisdiction_bonus
            if score <= 0:
                continue
            scored.append(
                RetrievedChunk(
                    id=chunk.id,
                    policy_id=chunk.policy_id,
                    text=chunk.text,
                    section=chunk.section,
                    page_reference=chunk.page_reference,
                    source_url=policy.source_url,
                    metadata={
                        **(chunk.metadata_json or {}),
                        "source_url": policy.source_url,
                        "jurisdiction": policy.jurisdiction,
                        "policy_name": policy.name,
                    },
                    score=float(score),
                    embedding_id=chunk.embedding_id,
                )
            )
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]
