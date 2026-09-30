from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.services import eligibility_service, result_service

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("/{result_id}", response_model=dict)
def read_result(result_id: str, session: Session = Depends(get_session)):
    record = eligibility_service.get_result(session, result_id)
    if record is None:
        raise HTTPException(status_code=404, detail={"code": "result_not_found", "message": "Result not found"})
    return {"data": result_service.to_read_model(record).model_dump()}
