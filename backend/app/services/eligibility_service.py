from sqlmodel import Session

from app.models.entities import EligibilityResult
from app.rules.engine import evaluate_policy
from app.schemas.eligibility import EligibilityResultRead, PolicyEvaluation
from app.services import document_service, policy_service
from app.services.profile_service import get_profile
from app.services.retrieval_service import search_policies
from ai.rag.retriever import RetrievedChunk


def evaluate_profile(session: Session, profile_id: str, query: str | None = None) -> EligibilityResult:
    profile = get_profile(session, profile_id)
    if profile is None:
        raise ValueError("profile_not_found")
    documents = document_service.list_documents(session, profile_id)
    chunk_reads, policies = search_policies(session, profile, query)
    retrieved = [
        RetrievedChunk(
            id=chunk.id,
            policy_id=chunk.policy_id,
            text=chunk.text,
            section=chunk.section,
            page_reference=chunk.page_reference,
            source_url=chunk.source_url,
            metadata=chunk.metadata or {},
            embedding_id=chunk.embedding_id,
        )
        for chunk in chunk_reads
    ]
    evaluations: list[PolicyEvaluation] = []
    for policy_read in policies:
        policy = policy_service.get_policy(session, policy_read.id)
        if policy is None:
            continue
        evaluations.append(evaluate_policy(session, profile, policy, documents, retrieved))
    payload = EligibilityResultRead(
        id="",
        profile_id=profile_id,
        policies=evaluations,
    )
    record = EligibilityResult(profile_id=profile_id, payload=payload.model_dump(mode="json"))
    session.add(record)
    session.commit()
    session.refresh(record)
    payload_dict = record.payload
    payload_dict["id"] = record.id
    record.payload = payload_dict
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_result(session: Session, result_id: str) -> EligibilityResult | None:
    return session.get(EligibilityResult, result_id)
