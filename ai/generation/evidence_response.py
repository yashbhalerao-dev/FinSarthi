from app.core.enums import OverallStatus
from app.schemas.eligibility import PolicyEvaluation


def build_explanation(evaluation: PolicyEvaluation) -> str:
    if not evaluation.evidence:
        return (
            "Insufficient retrieved evidence to support a narrative explanation. "
            f"Python rules still produced {evaluation.overall_status.value}. "
            "No policy facts or benefits were invented."
        )
    status = evaluation.overall_status
    if status == OverallStatus.ELIGIBLE:
        lead = f"Python rules classified this synthetic demo policy as {status.value}."
    elif status == OverallStatus.NOT_ELIGIBLE:
        failed = [item.field for item in evaluation.conditions if item.status.value == "NOT_SATISFIED"]
        lead = f"Python rules classified this as {status.value} because failed conditions: {', '.join(failed) or 'n/a'}."
    else:
        uncertain = [item.field for item in evaluation.conditions if item.status.value == "NEEDS_VERIFICATION"]
        lead = f"Python rules require verification for: {', '.join(uncertain) or 'insufficient evidence'}."
    citations = [item.section or item.chunk_id or "" for item in evaluation.evidence[:3]]
    citation_text = "; ".join(part for part in citations if part)
    suffix = f" Evidence references: {citation_text}." if citation_text else ""
    if evaluation.synthetic:
        suffix += " This evaluation uses a synthetic demo policy, not an official government scheme."
    return lead + suffix


def generate_explanation(evaluation: PolicyEvaluation) -> str:
    """Explain rule results. Never changes eligibility; optional LLM is evidence-only."""
    template = build_explanation(evaluation)
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.llm_api_key:
        return template
    try:
        from ai.generation.llm import explain_with_llm

        return explain_with_llm(evaluation, template)
    except Exception:
        return template
