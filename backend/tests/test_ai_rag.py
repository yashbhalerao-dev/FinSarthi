import json

from ai.ocr.adapter import get_ocr_adapter
from ai.ocr.demo_ocr import LocalDemoOCRAdapter
from ai.generation.evidence_response import generate_explanation
from ai.rag.factory import get_retriever
from app.core.config import get_settings
from app.models.entities import ApplicantProfile
from app.rules.engine import evaluate_policy
from app.services.policy_service import get_policy


def test_local_ocr_extracts_demo_json() -> None:
    adapter = LocalDemoOCRAdapter()
    payload = json.dumps(
        {
            "document_type": "income_certificate",
            "confidence": 0.91,
            "extracted_fields": {"income": 180000, "state": "Maharashtra", "age": 30},
        }
    ).encode("utf-8")
    result = adapter.extract("demo-a-note.json", payload)
    assert result.document_type == "income_certificate"
    assert result.extracted_fields["income"] == 180000
    assert result.confidence >= 0.9
    assert result.uncertain_fields == []
    assert result.extraction_status == "processed"


def test_ocr_provider_config_uses_local_adapter() -> None:
    adapter = get_ocr_adapter("local")
    assert isinstance(adapter, LocalDemoOCRAdapter)
    named = adapter.extract("demo-c-identity.json", b"placeholder")
    assert "income" in named.uncertain_fields
    assert named.extraction_status == "processed"


def test_retrieval_fallback_without_pinecone(session) -> None:
    assert get_settings().pinecone_enabled is False
    profile = ApplicantProfile(
        applicant_type="individual",
        state="Maharashtra",
        occupation="salaried",
        uncertain_fields=[],
        source_evidence=[],
    )
    hits = get_retriever(session).retrieve(
        "individual Maharashtra financial assistance",
        jurisdiction="Maharashtra",
        applicant_type="individual",
    )
    assert hits
    hit = hits[0]
    assert hit.policy_id
    assert hit.id
    assert hit.text
    assert hit.source_url
    assert "source_url" in hit.metadata


def test_evidence_structure_from_rules(session) -> None:
    profile = ApplicantProfile(
        applicant_type="individual",
        age=28,
        state="Maharashtra",
        income=200000,
        uncertain_fields=[],
        source_evidence=[],
    )
    policy = get_policy(session, "synthetic-demo-alpha")
    result = evaluate_policy(session, profile, policy, [])
    assert result.evidence
    item = result.evidence[0]
    assert item.policy_id == policy.id
    assert item.chunk_id
    assert item.text
    assert item.source_url
    assert item.section or item.page_reference
    assert isinstance(item.metadata, dict)
    assert "Python rules" in result.explanation or "insufficient" in result.explanation.lower()


def test_unsupported_benefit_not_invented(session) -> None:
    profile = ApplicantProfile(
        applicant_type="individual",
        age=28,
        state="Karnataka",
        income=200000,
        uncertain_fields=[],
        source_evidence=[],
    )
    policy = get_policy(session, "synthetic-demo-gamma")
    result = evaluate_policy(session, profile, policy, [])
    assert result.benefit.supported_by_source is False
    assert result.benefit.amount is None


def test_needs_verification_when_information_insufficient(session) -> None:
    profile = ApplicantProfile(
        applicant_type="individual",
        age=41,
        state="Maharashtra",
        income=None,
        uncertain_fields=["income"],
        source_evidence=[],
    )
    policy = get_policy(session, "synthetic-demo-alpha")
    result = evaluate_policy(session, profile, policy, [])
    assert result.overall_status.value == "NEEDS_VERIFICATION"
    explanation = generate_explanation(result)
    assert "Python rules" in explanation or "verification" in explanation.lower()
