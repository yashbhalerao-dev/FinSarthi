from sqlmodel import Session, select

from ai.ocr.extractor import extract_document
from app.core.config import get_settings
from app.models.entities import Document
from app.services.storage import LocalDocumentStorage


def upload_document(session: Session, profile_id: str, filename: str, payload: bytes) -> Document:
    storage = LocalDocumentStorage(get_settings().upload_dir)
    reference = storage.save(profile_id, filename, payload)
    document = Document(
        profile_id=profile_id,
        filename=filename,
        storage_reference=reference,
        extraction_status="pending",
    )
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


def process_document(session: Session, document: Document) -> Document:
    storage = LocalDocumentStorage(get_settings().upload_dir)
    payload = storage.read(document.storage_reference)
    result = extract_document(document.filename, payload)
    document.document_type = result.document_type
    document.extracted_fields = result.extracted_fields
    document.confidence = result.confidence
    document.uncertain_fields = result.uncertain_fields
    document.extraction_status = result.extraction_status or "processed"
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


def get_document(session: Session, document_id: str) -> Document | None:
    return session.get(Document, document_id)


def list_documents(session: Session, profile_id: str) -> list[Document]:
    return list(session.exec(select(Document).where(Document.profile_id == profile_id)).all())
