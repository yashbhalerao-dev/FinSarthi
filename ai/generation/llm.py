import httpx

from app.core.config import get_settings
from app.schemas.eligibility import PolicyEvaluation


def explain_with_llm(evaluation: PolicyEvaluation, fallback: str) -> str:
    settings = get_settings()
    if not settings.llm_api_key:
        return fallback
    evidence_lines = []
    for item in evaluation.evidence:
        evidence_lines.append(
            f"[{item.section or item.chunk_id}] {item.text} (source={item.source_url})"
        )
    prompt = (
        "You explain eligibility results. You must not decide eligibility. "
        f"Authoritative Python-rule status: {evaluation.overall_status.value}. "
        "Use only the evidence lines. If evidence is insufficient, say so. "
        "Do not invent benefits, thresholds, URLs, or scheme names.\n\n"
        f"Conditions: {evaluation.conditions}\n"
        f"Evidence:\n" + ("\n".join(evidence_lines) or "(none)")
    )
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": settings.llm_model or "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You only rephrase provided rule results and evidence."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }
    with httpx.Client(timeout=20.0) as client:
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=body,
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"].strip()
    if not text:
        return fallback
    return text
