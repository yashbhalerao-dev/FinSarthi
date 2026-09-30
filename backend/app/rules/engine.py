from sqlmodel import Session, select

from ai.generation.evidence_response import generate_explanation
from ai.rag.retriever import RetrievedChunk
from app.core.enums import OverallStatus
from app.models.entities import ApplicantProfile, Document, Policy, PolicyChunk
from app.rules.base import evaluate_condition, overall_status
from app.schemas.eligibility import (
    ApplicationRoute,
    BenefitResult,
    ConditionResult,
    EvidenceItem,
    PolicyEvaluation,
)


def missing_documents(policy: Policy, documents: list[Document]) -> list[str]:
    available = {doc.document_type for doc in documents if doc.extraction_status == "processed"}
    return [name for name in policy.required_documents or [] if name not in available]


def evidence_for_condition(chunks: list[PolicyChunk], field: str) -> PolicyChunk | None:
    needle = field.replace("_", " ").lower()
    for chunk in chunks:
        hay = f"{chunk.section or ''} {chunk.text}".lower()
        if needle in hay or field.lower() in hay:
            return chunk
    return chunks[0] if chunks else None


def benefit_from_policy(policy: Policy) -> BenefitResult:
    raw = policy.benefit or {}
    supported = bool(raw.get("supported_by_source"))
    amount = raw.get("amount") if supported else None
    if not supported:
        return BenefitResult(amount=None, currency=None, basis=raw.get("basis"), supported_by_source=False)
    return BenefitResult(
        amount=amount,
        currency=raw.get("currency"),
        basis=raw.get("basis"),
        supported_by_source=True,
    )


def evaluate_policy(
    session: Session,
    profile: ApplicantProfile,
    policy: Policy,
    documents: list[Document],
    retrieved: list[RetrievedChunk] | None = None,
) -> PolicyEvaluation:
    db_chunks = list(session.exec(select(PolicyChunk).where(PolicyChunk.policy_id == policy.id)).all())
    retrieved = [item for item in (retrieved or []) if item.policy_id == policy.id]
    conditions: list[ConditionResult] = []
    evidence_items: list[EvidenceItem] = []

    def evidence_chunk_for_field(field: str) -> tuple[str | None, EvidenceItem | None]:
        needle = field.replace("_", " ").lower()
        for hit in retrieved:
            hay = f"{hit.section or ''} {hit.text}".lower()
            if needle in hay or field.lower() in hay:
                return hit.id, _from_retrieved(policy, hit)
        chunk = evidence_for_condition(db_chunks, field)
        if chunk:
            return chunk.id, _from_db_chunk(policy, chunk)
        if retrieved:
            hit = retrieved[0]
            return hit.id, _from_retrieved(policy, hit)
        return None, None

    for spec in policy.conditions or []:
        evidence_id, evidence_item = evidence_chunk_for_field(spec.get("field", ""))
        result = evaluate_condition(profile, spec, evidence_id)
        conditions.append(result)
        if evidence_item:
            evidence_items.append(evidence_item)

    unique_evidence = []
    seen = set()
    for item in evidence_items:
        key = item.chunk_id or item.text
        if key in seen:
            continue
        seen.add(key)
        unique_evidence.append(item)

    missing = missing_documents(policy, documents)
    status = overall_status(conditions)
    review_required = status == OverallStatus.NEEDS_VERIFICATION or bool(missing)
    evaluation = PolicyEvaluation(
        policy_id=policy.id,
        policy_name=policy.name,
        synthetic=policy.synthetic,
        overall_status=status,
        conditions=conditions,
        benefit=benefit_from_policy(policy),
        required_documents=list(policy.required_documents or []),
        missing_documents=missing,
        evidence=unique_evidence,
        application_route=ApplicationRoute(
            url=(policy.application_route or {}).get("url"),
            steps=list((policy.application_route or {}).get("steps") or []),
        ),
        review_required=review_required,
        explanation="",
    )
    evaluation.explanation = generate_explanation(evaluation)
    return evaluation


def _from_retrieved(policy: Policy, hit: RetrievedChunk) -> EvidenceItem:
    return EvidenceItem(
        policy_id=policy.id,
        chunk_id=hit.id,
        source_url=hit.source_url or policy.source_url,
        section=hit.section,
        page_reference=hit.page_reference,
        text=hit.text,
        metadata=hit.metadata or {},
    )


def _from_db_chunk(policy: Policy, chunk: PolicyChunk) -> EvidenceItem:
    return EvidenceItem(
        policy_id=policy.id,
        chunk_id=chunk.id,
        source_url=policy.source_url,
        section=chunk.section,
        page_reference=chunk.page_reference,
        text=chunk.text,
        metadata=chunk.metadata_json or {},
    )
