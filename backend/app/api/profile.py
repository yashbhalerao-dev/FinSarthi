from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate
from app.services import profile_service

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.post("", response_model=dict)
def create_profile(payload: ProfileCreate, session: Session = Depends(get_session)):
    profile = profile_service.create_profile(session, payload)
    return {"data": ProfileRead.model_validate(profile).model_dump()}


@router.get("/{profile_id}", response_model=dict)
def read_profile(profile_id: str, session: Session = Depends(get_session)):
    profile = profile_service.get_profile(session, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found", "message": "Profile not found"})
    return {"data": ProfileRead.model_validate(profile).model_dump()}


@router.put("/{profile_id}", response_model=dict)
def replace_profile(profile_id: str, payload: ProfileUpdate, session: Session = Depends(get_session)):
    profile = profile_service.get_profile(session, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found", "message": "Profile not found"})
    profile = profile_service.update_profile(session, profile, payload)
    return {"data": ProfileRead.model_validate(profile).model_dump()}
