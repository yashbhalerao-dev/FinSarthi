import json
import sys
from pathlib import Path

from sqlmodel import Session, select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.core.db import engine, init_db  # noqa: E402
from app.models.entities import ApplicantProfile, EligibilityResult  # noqa: E402
from app.schemas.profile import ProfileCreate  # noqa: E402
from app.services import document_service, eligibility_service, policy_service, profile_service  # noqa: E402

DEMO_CASES = [
    {
        "id": "demo-a",
        "label": "SYNTHETIC DEMO A — expected ELIGIBLE",
        "filename": "demo-a-income.json",
        "document_json": {
            "document_type": "income_certificate",
            "confidence": 0.93,
            "uncertain_fields": [],
            "extracted_fields": {
                "applicant_type": "individual",
                "age": 28,
                "state": "Maharashtra",
                "district": "Pune",
                "income": 200000,
                "occupation": "salaried",
            },
        },
        "extra_docs": [
            {
                "filename": "demo-a-identity.json",
                "body": {
                    "document_type": "identity_proof",
                    "confidence": 0.9,
                    "extracted_fields": {"state": "Maharashtra"},
                },
            }
        ],
        "profile": {
            "id": "demo-a",
            "applicant_type": "individual",
            "age": 28,
            "state": "Maharashtra",
            "district": "Pune",
            "income": 200000,
            "occupation": "salaried",
            "uncertain_fields": [],
            "source_evidence": [],
        },
    },
    {
        "id": "demo-b",
        "label": "SYNTHETIC DEMO B — expected NOT_ELIGIBLE",
        "filename": "demo-b-registration.json",
        "document_json": {
            "document_type": "business_registration",
            "confidence": 0.9,
            "extracted_fields": {
                "applicant_type": "small_business",
                "state": "Maharashtra",
                "business_type": "trading",
                "registration_status": "registered",
                "turnover": 5000000,
            },
        },
        "extra_docs": [
            {
                "filename": "demo-b-bank.json",
                "body": {"document_type": "bank_statement", "confidence": 0.88, "extracted_fields": {}},
            }
        ],
        "profile": {
            "id": "demo-b",
            "applicant_type": "small_business",
            "state": "Maharashtra",
            "occupation": "owner",
            "business_type": "trading",
            "registration_status": "registered",
            "turnover": 5000000,
            "investment": 800000,
            "uncertain_fields": [],
            "source_evidence": [],
        },
    },
    {
        "id": "demo-c",
        "label": "SYNTHETIC DEMO C — expected NEEDS_VERIFICATION",
        "filename": "demo-c-identity.json",
        "document_json": {
            "document_type": "identity_proof",
            "confidence": 0.4,
            "uncertain_fields": ["income"],
            "extracted_fields": {
                "applicant_type": "individual",
                "age": 41,
                "state": "Maharashtra",
                "occupation": "self-employed",
            },
        },
        "extra_docs": [],
        "profile": {
            "id": "demo-c",
            "applicant_type": "individual",
            "age": 41,
            "state": "Maharashtra",
            "occupation": "self-employed",
            "uncertain_fields": ["income"],
            "source_evidence": [],
        },
    },
]


def _replace_profile(session: Session, payload: dict) -> None:
    existing = session.get(ApplicantProfile, payload["id"])
    if existing:
        session.delete(existing)
        session.commit()
    profile_service.create_profile(session, ProfileCreate(**payload))


def seed() -> None:
    init_db()
    with Session(engine) as session:
        policy_service.upsert_policies(session)
        for case in DEMO_CASES:
            for old in document_service.list_documents(session, case["id"]):
                session.delete(old)
            session.commit()
            _replace_profile(session, case["profile"])
            body = json.dumps(case["document_json"]).encode("utf-8")
            document = document_service.upload_document(session, case["id"], case["filename"], body)
            document_service.process_document(session, document)
            for extra in case["extra_docs"]:
                extra_doc = document_service.upload_document(
                    session,
                    case["id"],
                    extra["filename"],
                    json.dumps(extra["body"]).encode("utf-8"),
                )
                document_service.process_document(session, extra_doc)
            result = eligibility_service.evaluate_profile(session, case["id"])
            statuses = {
                item["policy_id"]: item["overall_status"] for item in result.payload.get("policies", [])
            }
            print(f"{case['label']}: result_id={result.id} statuses={statuses}")


if __name__ == "__main__":
    seed()
