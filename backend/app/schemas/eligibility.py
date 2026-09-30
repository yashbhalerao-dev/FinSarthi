from typing import Any, Optional

from pydantic import BaseModel

from app.core.enums import ConditionStatus, OverallStatus


class ConditionResult(BaseModel):
    field: str
    operator: str
    expected: Any
    actual: Any = None
    status: ConditionStatus
    evidence: Optional[str] = None
    reason: Optional[str] = None


class BenefitResult(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    basis: Optional[str] = None
    supported_by_source: bool = False


class EvidenceItem(BaseModel):
    policy_id: str
    chunk_id: Optional[str] = None
    source_url: str
    section: Optional[str] = None
    page_reference: Optional[str] = None
    text: Optional[str] = None
    metadata: dict[str, Any] = {}


class ApplicationRoute(BaseModel):
    url: Optional[str] = None
    steps: list[str] = []


class PolicyEvaluation(BaseModel):
    policy_id: str
    policy_name: str
    synthetic: bool = True
    overall_status: OverallStatus
    conditions: list[ConditionResult]
    benefit: BenefitResult
    required_documents: list[str]
    missing_documents: list[str]
    evidence: list[EvidenceItem]
    application_route: ApplicationRoute
    review_required: bool
    explanation: str


class EligibilityResultRead(BaseModel):
    id: str
    profile_id: str
    policies: list[PolicyEvaluation]


class EvaluateRequest(BaseModel):
    profile_id: str
    query: Optional[str] = None
