from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

ApplicantTypeLiteral = Literal["individual", "small_business"]


class ProfileBase(BaseModel):
    applicant_type: ApplicantTypeLiteral
    age: Optional[int] = Field(default=None, ge=0, le=120)
    state: Optional[str] = None
    district: Optional[str] = None
    income: Optional[float] = Field(default=None, ge=0)
    occupation: Optional[str] = None
    category: Optional[str] = None
    business_type: Optional[str] = None
    registration_status: Optional[str] = None
    turnover: Optional[float] = Field(default=None, ge=0)
    investment: Optional[float] = Field(default=None, ge=0)
    uncertain_fields: list[str] = Field(default_factory=list)
    source_evidence: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("applicant_type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value not in ("individual", "small_business"):
            raise ValueError("applicant_type must be individual or small_business")
        return value


class ProfileCreate(ProfileBase):
    id: Optional[str] = None


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    id: str

    model_config = {"from_attributes": True}
