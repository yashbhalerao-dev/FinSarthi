from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session

from app.core.db import get_session
from app.schemas.document import DocumentProcessRequest, DocumentRead
from app.schemas.profile import ProfileRead
from app.services import document_service, profile_service

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=dict)
def list_documents(profile_id: str, session: Session = Depends(get_session)):
    profile = profile_service.get_profile(session, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found", "message": "Profile not found"})
    documents = document_service.list_documents(session, profile_id)
    return {"data": [DocumentRead.model_validate(item).model_dump() for item in documents]}


@router.post("/upload", response_model=dict)
async def upload_document(
    profile_id: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    profile = profile_service.get_profile(session, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found", "message": "Profile not found"})
    payload = await file.read()
    document = document_service.upload_document(session, profile_id, file.filename or "upload.bin", payload)
    return {"data": DocumentRead.model_validate(document).model_dump()}


@router.post("/process", response_model=dict)
def process_document(payload: DocumentProcessRequest, session: Session = Depends(get_session)):
    document = document_service.get_document(session, payload.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"code": "document_not_found", "message": "Document not found"})
    document = document_service.process_document(session, document)
    profile = profile_service.get_profile(session, document.profile_id)
    if profile is not None:
        profile_service.merge_extracted_fields(profile, document.extracted_fields, document.uncertain_fields)
        session.add(profile)
        session.commit()
        session.refresh(profile)
    return {
        "data": {
            "document": DocumentRead.model_validate(document).model_dump(),
            "profile": ProfileRead.model_validate(profile).model_dump() if profile else None,
        }
    }


@router.get("/{document_id}", response_model=dict)
def read_document(document_id: str, session: Session = Depends(get_session)):
    document = document_service.get_document(session, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"code": "document_not_found", "message": "Document not found"})
    return {"data": DocumentRead.model_validate(document).model_dump()}
