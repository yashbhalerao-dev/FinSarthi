import json
from typing import Any

from ai.ocr.adapter import OCRAdapter, OcrResult

_DEMO_MARKERS: dict[str, dict[str, Any]] = {
    "demo-a": {
        "document_type": "income_certificate",
        "extracted_fields": {
            "applicant_type": "individual",
            "age": 28,
            "state": "Maharashtra",
            "district": "Pune",
            "income": 200000,
            "occupation": "salaried",
            "category": "general",
        },
        "confidence": 0.92,
        "uncertain_fields": [],
    },
    "demo-b": {
        "document_type": "business_registration",
        "extracted_fields": {
            "applicant_type": "small_business",
            "state": "Maharashtra",
            "district": "Nagpur",
            "occupation": "owner",
            "business_type": "trading",
            "registration_status": "registered",
            "turnover": 5000000,
            "investment": 800000,
        },
        "confidence": 0.9,
        "uncertain_fields": [],
    },
    "demo-c": {
        "document_type": "identity_proof",
        "extracted_fields": {
            "applicant_type": "individual",
            "age": 41,
            "state": "Maharashtra",
            "occupation": "self-employed",
        },
        "confidence": 0.45,
        "uncertain_fields": ["income", "district"],
    },
}


class LocalDemoOCRAdapter(OCRAdapter):
    """Deterministic local extractor for synthetic demo files. Not a production OCR engine."""

    provider_id = "local"

    def extract(self, filename: str, payload: bytes) -> OcrResult:
        name = filename.lower()
        text = _decode(payload)
        parsed = _try_json(text)
        if parsed:
            fields = parsed.get("extracted_fields") or parsed
            uncertain = list(parsed.get("uncertain_fields") or [])
            if parsed.get("income") is None and "income" not in fields:
                if "income" not in uncertain and parsed.get("mark_income_uncertain"):
                    uncertain.append("income")
            extracted = _normalize_fields(fields if isinstance(fields, dict) else parsed)
            return OcrResult(
                document_type=str(parsed.get("document_type") or "supporting_document"),
                extracted_fields=extracted,
                confidence=float(parsed.get("confidence") or 0.8),
                uncertain_fields=uncertain,
                extraction_status="processed",
                raw_text=text,
            )

        for marker, preset in _DEMO_MARKERS.items():
            if marker in name or marker.replace("-", "_") in name:
                return OcrResult(
                    document_type=preset["document_type"],
                    extracted_fields=dict(preset["extracted_fields"]),
                    confidence=float(preset["confidence"]),
                    uncertain_fields=list(preset["uncertain_fields"]),
                    extraction_status="processed",
                    raw_text=text or marker,
                )

        fields: dict[str, Any] = {}
        uncertain: list[str] = []
        lowered = text.lower()
        if "maharashtra" in lowered:
            fields["state"] = "Maharashtra"
        if "karnataka" in lowered:
            fields["state"] = "Karnataka"
        if "income" in lowered and "unknown" in lowered:
            uncertain.append("income")
        if not fields:
            uncertain.extend(["income", "state"])
        confidence = 0.35 if uncertain else 0.6
        return OcrResult(
            document_type="unknown",
            extracted_fields=fields,
            confidence=confidence,
            uncertain_fields=uncertain,
            extraction_status="processed" if fields or uncertain else "failed",
            raw_text=text,
        )


DemoOCRAdapter = LocalDemoOCRAdapter


def _decode(payload: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            continue
    return ""


def _try_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text.startswith("{"):
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _normalize_fields(raw: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "applicant_type",
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
        "document_type",
    }
    out: dict[str, Any] = {}
    for key, value in raw.items():
        if key in allowed and value is not None:
            out[key] = value
    return out
