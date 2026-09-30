from typing import Any, Optional

from pydantic import BaseModel


class PolicyChunkRead(BaseModel):
    id: str
    policy_id: str
    text: str
    section: Optional[str] = None
    page_reference: Optional[str] = None
    source_url: Optional[str] = None
    metadata: dict[str, Any] = {}
    embedding_id: Optional[str] = None


class PolicyRead(BaseModel):
    id: str
    name: str
    issuing_authority: str
    jurisdiction: str
    category: str
    applicant_type: str
    source_url: str
    source_document: str
    version: Optional[str] = None
    effective_date: Optional[str] = None
    verified_at: Optional[str] = None
    status: str
    conditions: list[dict[str, Any]]
    required_documents: list[str]
    benefit: Optional[dict[str, Any]] = None
    application_route: dict[str, Any]
    synthetic: bool

    model_config = {"from_attributes": True}


class PolicySearchRequest(BaseModel):
    profile_id: str
    query: Optional[str] = None


class PolicySearchResponse(BaseModel):
    chunks: list[PolicyChunkRead]
    policies: list[PolicyRead]
