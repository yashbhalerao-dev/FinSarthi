from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OcrResult:
    document_type: str
    extracted_fields: dict[str, Any]
    confidence: float
    uncertain_fields: list[str] = field(default_factory=list)
    extraction_status: str = "processed"
    raw_text: str = ""


class OCRAdapter(ABC):
    provider_id: str

    @abstractmethod
    def extract(self, filename: str, payload: bytes) -> OcrResult:
        raise NotImplementedError


def get_ocr_adapter(provider: str | None = None) -> OCRAdapter:
    from app.core.config import get_settings
    from ai.ocr.demo_ocr import LocalDemoOCRAdapter

    chosen = (provider or get_settings().ocr_provider or "local").lower()
    adapters = {
        "local": LocalDemoOCRAdapter,
        "demo": LocalDemoOCRAdapter,
        "stub": LocalDemoOCRAdapter,
    }
    factory = adapters.get(chosen, LocalDemoOCRAdapter)
    return factory()
