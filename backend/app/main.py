import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api import documents, eligibility, health, policies, profile, results
from app.core.config import get_settings
from app.core.db import init_db
from app.services.policy_service import upsert_policies
from app.core.db import engine
from sqlmodel import Session

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with Session(engine) as session:
        try:
            upsert_policies(session)
        except FileNotFoundError:
            pass
    yield


app = FastAPI(
    title="FinSarthi API",
    description="Financial Policy Discovery, Eligibility & Application Assistant (50% prototype).",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(profile.router)
app.include_router(documents.router)
app.include_router(policies.router)
app.include_router(eligibility.router)
app.include_router(results.router)
