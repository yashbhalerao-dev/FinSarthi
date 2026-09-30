from typing import Any

from app.core.enums import ConditionStatus, OverallStatus
from app.schemas.eligibility import ConditionResult

PROFILE_FIELD_MAP = {
    "annual_income": "income",
    "income": "income",
    "age": "age",
    "state": "state",
    "district": "district",
    "occupation": "occupation",
    "category": "category",
    "applicant_type": "applicant_type",
    "business_type": "business_type",
    "registration_status": "registration_status",
    "turnover": "turnover",
    "investment": "investment",
}


def profile_value(profile: Any, field: str) -> Any:
    attr = PROFILE_FIELD_MAP.get(field, field)
    return getattr(profile, attr, None)


def has_conflict(profile: Any, field: str) -> bool:
    attr = PROFILE_FIELD_MAP.get(field, field)
    values = []
    for item in profile.source_evidence or []:
        if item.get("field") in {field, attr}:
            values.append(item.get("value"))
    unique = {str(value) for value in values if value is not None}
    if len(unique) > 1:
        return True
    current = getattr(profile, attr, None)
    if current is not None and unique and str(current) not in unique:
        return True
    return False


def compare(actual: Any, operator: str, expected: Any) -> bool:
    if operator == "<=":
        return actual <= expected
    if operator == ">=":
        return actual >= expected
    if operator == "<":
        return actual < expected
    if operator == ">":
        return actual > expected
    if operator == "==":
        if isinstance(expected, str) and isinstance(actual, str):
            return actual.strip().lower() == expected.strip().lower()
        return actual == expected
    if operator == "!=":
        return actual != expected
    if operator == "in":
        return actual in expected
    raise ValueError(f"Unsupported operator: {operator}")


def evaluate_condition(profile: Any, spec: dict[str, Any], evidence_id: str | None) -> ConditionResult:
    field = spec["field"]
    operator = spec["operator"]
    expected = spec["expected"]
    mapped = PROFILE_FIELD_MAP.get(field, field)
    uncertain = {name.lower() for name in (profile.uncertain_fields or [])}
    if mapped.lower() in uncertain or field.lower() in uncertain:
        return ConditionResult(
            field=field,
            operator=operator,
            expected=expected,
            actual=profile_value(profile, field),
            status=ConditionStatus.NEEDS_VERIFICATION,
            evidence=evidence_id,
            reason="Field is marked uncertain on the applicant profile.",
        )
    if has_conflict(profile, field):
        return ConditionResult(
            field=field,
            operator=operator,
            expected=expected,
            actual=profile_value(profile, field),
            status=ConditionStatus.NEEDS_VERIFICATION,
            evidence=evidence_id,
            reason="Conflicting evidence for this field.",
        )
    actual = profile_value(profile, field)
    if actual is None or actual == "":
        return ConditionResult(
            field=field,
            operator=operator,
            expected=expected,
            actual=None,
            status=ConditionStatus.NEEDS_VERIFICATION,
            evidence=evidence_id,
            reason="Critical field is missing.",
        )
    try:
        ok = compare(actual, operator, expected)
    except TypeError:
        return ConditionResult(
            field=field,
            operator=operator,
            expected=expected,
            actual=actual,
            status=ConditionStatus.NEEDS_VERIFICATION,
            evidence=evidence_id,
            reason="Field could not be compared against the rule.",
        )
    return ConditionResult(
        field=field,
        operator=operator,
        expected=expected,
        actual=actual,
        status=ConditionStatus.SATISFIED if ok else ConditionStatus.NOT_SATISFIED,
        evidence=evidence_id,
        reason="Condition met." if ok else "Condition not met.",
    )


def overall_status(conditions: list[ConditionResult]) -> OverallStatus:
    if any(item.status == ConditionStatus.NOT_SATISFIED for item in conditions):
        return OverallStatus.NOT_ELIGIBLE
    if any(item.status == ConditionStatus.NEEDS_VERIFICATION for item in conditions):
        return OverallStatus.NEEDS_VERIFICATION
    return OverallStatus.ELIGIBLE
