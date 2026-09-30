from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: str
    profile_id: str
    filename: str
    document_type: str
    storage_reference: str
    extraction_status: str
    extracted_fields: dict[str, Any]
    confidence: float
    uncertain_fields: list[str]
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DocumentProcessRequest(BaseModel):
    document_id: str


class ProfileFromDocumentsRequest(BaseModel):
    profile_id: str
    merge: bool = True
