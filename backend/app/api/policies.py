from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.schemas.policy import PolicyRead, PolicySearchRequest
from app.services import policy_service, profile_service
from app.services.retrieval_service import search_policies

router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.get("", response_model=dict)
def list_policies(session: Session = Depends(get_session)):
    policies = [PolicyRead.model_validate(item).model_dump() for item in policy_service.list_policies(session)]
    return {"data": policies}


@router.post("/search", response_model=dict)
def search(payload: PolicySearchRequest, session: Session = Depends(get_session)):
    profile = profile_service.get_profile(session, payload.profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found", "message": "Profile not found"})
    chunks, policies = search_policies(session, profile, payload.query)
    return {
        "data": {
            "chunks": [chunk.model_dump() for chunk in chunks],
            "policies": [policy.model_dump() for policy in policies],
        }
    }


@router.get("/{policy_id}", response_model=dict)
def read_policy(policy_id: str, session: Session = Depends(get_session)):
    policy = policy_service.get_policy(session, policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail={"code": "policy_not_found", "message": "Policy not found"})
    return {"data": PolicyRead.model_validate(policy).model_dump()}
