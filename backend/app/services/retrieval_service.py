from sqlmodel import Session

from ai.rag.factory import get_retriever
from app.models.entities import ApplicantProfile, Policy
from app.services import policy_service
from app.schemas.policy import PolicyChunkRead, PolicyRead


def search_policies(session: Session, profile: ApplicantProfile, query: str | None):
    retriever = get_retriever(session)
    built_query = query or " ".join(
        str(part)
        for part in [
            profile.applicant_type,
            profile.state,
            profile.occupation,
            profile.business_type,
            profile.category,
            "financial assistance",
        ]
        if part
    )
    chunks = retriever.retrieve(
        built_query,
        jurisdiction=profile.state,
        applicant_type=profile.applicant_type,
    )
    policies: list[Policy] = []
    seen = set()
    for chunk in chunks:
        if chunk.policy_id in seen:
            continue
        policy = policy_service.get_policy(session, chunk.policy_id)
        if policy:
            seen.add(policy.id)
            policies.append(policy)
    if not policies:
        for policy in policy_service.list_policies(session):
            if policy.applicant_type in {profile.applicant_type, "any"}:
                policies.append(policy)
    chunk_reads = [
        PolicyChunkRead(
            id=chunk.id,
            policy_id=chunk.policy_id,
            text=chunk.text,
            section=chunk.section,
            page_reference=chunk.page_reference,
            source_url=chunk.source_url,
            metadata=chunk.metadata,
            embedding_id=chunk.embedding_id,
        )
        for chunk in chunks
    ]
    return chunk_reads, [PolicyRead.model_validate(policy) for policy in policies]
