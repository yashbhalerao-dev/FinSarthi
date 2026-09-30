from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.schemas.eligibility import EvaluateRequest
from app.services import eligibility_service, result_service

router = APIRouter(prefix="/api/eligibility", tags=["eligibility"])


@router.post("/evaluate", response_model=dict)
def evaluate(payload: EvaluateRequest, session: Session = Depends(get_session)):
    try:
        record = eligibility_service.evaluate_profile(session, payload.profile_id, payload.query)
    except ValueError:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found", "message": "Profile not found"})
    return {"data": result_service.to_read_model(record).model_dump()}
