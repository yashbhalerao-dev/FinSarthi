from app.models.entities import EligibilityResult
from app.schemas.eligibility import EligibilityResultRead


def to_read_model(record: EligibilityResult) -> EligibilityResultRead:
    payload = dict(record.payload or {})
    payload["id"] = record.id
    payload["profile_id"] = record.profile_id
    return EligibilityResultRead.model_validate(payload)
