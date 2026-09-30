from sqlmodel import Session

from app.models.entities import ApplicantProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate


def create_profile(session: Session, payload: ProfileCreate) -> ApplicantProfile:
    data = payload.model_dump()
    profile_id = data.pop("id", None)
    profile = ApplicantProfile(**data)
    if profile_id:
        profile.id = profile_id
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def update_profile(session: Session, profile: ApplicantProfile, payload: ProfileUpdate) -> ApplicantProfile:
    for key, value in payload.model_dump().items():
        setattr(profile, key, value)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def get_profile(session: Session, profile_id: str) -> ApplicantProfile | None:
    return session.get(ApplicantProfile, profile_id)


def merge_extracted_fields(profile: ApplicantProfile, fields: dict, uncertain: list[str]) -> ApplicantProfile:
    assignable = {
        "age",
        "state",
        "district",
        "income",
        "occupation",
        "category",
        "business_type",
        "registration_status",
        "turnover",
        "investment",
        "applicant_type",
    }
    for key, value in fields.items():
        if key in assignable and getattr(profile, key) in (None, "", []):
            setattr(profile, key, value)
    profile.uncertain_fields = sorted({*(profile.uncertain_fields or []), *uncertain})
    return profile
