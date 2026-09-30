from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


class ApplicantProfile(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    applicant_type: str
    age: Optional[int] = None
    state: Optional[str] = None
    district: Optional[str] = None
    income: Optional[float] = None
    occupation: Optional[str] = None
    category: Optional[str] = None
    business_type: Optional[str] = None
    registration_status: Optional[str] = None
    turnover: Optional[float] = None
    investment: Optional[float] = None
    uncertain_fields: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    source_evidence: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utcnow)


class Document(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    profile_id: str = Field(index=True)
    filename: str
    document_type: str = "unknown"
    storage_reference: str
    extraction_status: str = "pending"
    extracted_fields: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    confidence: float = 0.0
    uncertain_fields: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    uploaded_at: datetime = Field(default_factory=utcnow)


class Policy(SQLModel, table=True):
    id: str = Field(primary_key=True)
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
    status: str = "synthetic_demo"
    conditions: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    required_documents: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    benefit: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    application_route: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    synthetic: bool = True


class PolicyChunk(SQLModel, table=True):
    id: str = Field(primary_key=True)
    policy_id: str = Field(index=True)
    text: str
    section: Optional[str] = None
    page_reference: Optional[str] = None
    metadata_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    embedding_id: Optional[str] = None


class EligibilityResult(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    profile_id: str = Field(index=True)
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utcnow)
