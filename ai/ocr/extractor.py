from ai.ocr.adapter import OcrResult, get_ocr_adapter


def extract_document(filename: str, payload: bytes, provider: str | None = None) -> OcrResult:
    adapter = get_ocr_adapter(provider)
    return adapter.extract(filename, payload)
