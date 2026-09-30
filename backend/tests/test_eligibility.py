from app.models.entities import ApplicantProfile, Document
from app.rules.engine import evaluate_policy
from app.services.policy_service import get_policy


def _docs(*types: str) -> list[Document]:
    return [
        Document(
            profile_id="x",
            filename=f"{name}.json",
            document_type=name,
            storage_reference=name,
            extraction_status="processed",
        )
        for name in types
    ]


def test_eligible_individual(session) -> None:
    profile = ApplicantProfile(
        applicant_type="individual",
        age=28,
        state="Maharashtra",
        income=200000,
        occupation="salaried",
        uncertain_fields=[],
        source_evidence=[],
    )
    policy = get_policy(session, "synthetic-demo-alpha")
    result = evaluate_policy(session, profile, policy, _docs("identity_proof", "income_certificate"))
    assert result.overall_status.value == "ELIGIBLE"
    assert result.benefit.amount == 15000
    assert result.benefit.supported_by_source is True
    assert result.missing_documents == []
    assert all(item.status.value == "SATISFIED" for item in result.conditions)


def test_not_eligible_failed_turnover(session) -> None:
    profile = ApplicantProfile(
        applicant_type="small_business",
        state="Maharashtra",
        registration_status="registered",
        turnover=5000000,
        uncertain_fields=[],
        source_evidence=[],
    )
    policy = get_policy(session, "synthetic-demo-beta")
    result = evaluate_policy(session, profile, policy, _docs("business_registration", "bank_statement"))
    assert result.overall_status.value == "NOT_ELIGIBLE"
    failed = [item for item in result.conditions if item.field == "turnover"]
    assert failed and failed[0].status.value == "NOT_SATISFIED"


def test_needs_verification_missing_income(session) -> None:
    profile = ApplicantProfile(
        applicant_type="individual",
        age=41,
        state="Maharashtra",
        income=None,
        uncertain_fields=[],
        source_evidence=[],
    )
    policy = get_policy(session, "synthetic-demo-alpha")
    result = evaluate_policy(session, profile, policy, _docs("identity_proof", "income_certificate"))
    assert result.overall_status.value == "NEEDS_VERIFICATION"
    income = next(item for item in result.conditions if item.field == "annual_income")
    assert income.status.value == "NEEDS_VERIFICATION"


def test_uncertain_field(session) -> None:
    profile = ApplicantProfile(
        applicant_type="individual",
        age=28,
        state="Maharashtra",
        income=200000,
        uncertain_fields=["income"],
        source_evidence=[],
    )
    policy = get_policy(session, "synthetic-demo-alpha")
    result = evaluate_policy(session, profile, policy, _docs("identity_proof", "income_certificate"))
    assert result.overall_status.value == "NEEDS_VERIFICATION"


def test_conflicting_information(session) -> None:
    profile = ApplicantProfile(
        applicant_type="individual",
        age=28,
        state="Maharashtra",
        income=200000,
        uncertain_fields=[],
        source_evidence=[
            {"field": "income", "value": 200000, "source": "doc-1"},
            {"field": "income", "value": 900000, "source": "doc-2"},
        ],
    )
    policy = get_policy(session, "synthetic-demo-alpha")
    result = evaluate_policy(session, profile, policy, _docs("identity_proof", "income_certificate"))
    assert result.overall_status.value == "NEEDS_VERIFICATION"


def test_wrong_jurisdiction(session) -> None:
    profile = ApplicantProfile(
        applicant_type="individual",
        age=28,
        state="Maharashtra",
        income=200000,
        uncertain_fields=[],
        source_evidence=[],
    )
    policy = get_policy(session, "synthetic-demo-gamma")
    result = evaluate_policy(session, profile, policy, _docs("identity_proof"))
    state = next(item for item in result.conditions if item.field == "state")
    assert state.status.value == "NOT_SATISFIED"
    assert result.overall_status.value == "NOT_ELIGIBLE"


def test_missing_documents(session) -> None:
    profile = ApplicantProfile(
        applicant_type="individual",
        age=28,
        state="Maharashtra",
        income=200000,
        uncertain_fields=[],
        source_evidence=[],
    )
    policy = get_policy(session, "synthetic-demo-alpha")
    result = evaluate_policy(session, profile, policy, _docs("identity_proof"))
    assert "income_certificate" in result.missing_documents
    assert result.review_required is True


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
    result = evaluate_policy(session, profile, policy, _docs("identity_proof"))
    assert result.benefit.supported_by_source is False
    assert result.benefit.amount is None


def test_evaluate_api_demo_states(client) -> None:
    eligible = client.post(
        "/api/profile",
        json={
            "applicant_type": "individual",
            "age": 28,
            "state": "Maharashtra",
            "income": 200000,
            "occupation": "salaried",
        },
    ).json()["data"]
    client.post(
        "/api/documents/upload",
        data={"profile_id": eligible["id"]},
        files={
            "file": (
                "identity.json",
                b'{"document_type":"identity_proof","extracted_fields":{}}',
                "application/json",
            )
        },
    )
    # upload returns id; process to set type
    # simpler: evaluate without those docs still runs rules
    result = client.post("/api/eligibility/evaluate", json={"profile_id": eligible["id"]})
    assert result.status_code == 200
    policies = result.json()["data"]["policies"]
    alpha = next(item for item in policies if item["policy_id"] == "synthetic-demo-alpha")
    assert alpha["overall_status"] == "ELIGIBLE"
    fetched = client.get(f"/api/results/{result.json()['data']['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["data"]["id"] == result.json()["data"]["id"]
