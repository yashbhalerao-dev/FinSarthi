import json
from pathlib import Path

from sqlmodel import Session, select

from app.models.entities import Policy, PolicyChunk


def corpus_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "schemes" / "synthetic_demo_policies.json"


def load_corpus_file() -> dict:
    path = corpus_path()
    return json.loads(path.read_text(encoding="utf-8"))


def upsert_policies(session: Session) -> list[Policy]:
    payload = load_corpus_file()
    stored: list[Policy] = []
    for raw in payload["policies"]:
        item = dict(raw)
        existing = session.get(Policy, item["id"])
        chunks = item.pop("chunks")
        if existing:
            for key, value in item.items():
                setattr(existing, key, value)
            policy = existing
            for old in session.exec(select(PolicyChunk).where(PolicyChunk.policy_id == policy.id)).all():
                session.delete(old)
        else:
            policy = Policy(**item)
            session.add(policy)
        for chunk in chunks:
            session.add(
                PolicyChunk(
                    id=chunk["id"],
                    policy_id=policy.id,
                    text=chunk["text"],
                    section=chunk.get("section"),
                    page_reference=chunk.get("page_reference"),
                    metadata_json=chunk.get("metadata") or {},
                    embedding_id=chunk.get("embedding_id"),
                )
            )
        stored.append(policy)
    session.commit()
    return stored


def get_policy(session: Session, policy_id: str) -> Policy | None:
    return session.get(Policy, policy_id)


def list_policies(session: Session) -> list[Policy]:
    return list(session.exec(select(Policy)).all())


def chunks_for_policy(session: Session, policy_id: str) -> list[PolicyChunk]:
    return list(session.exec(select(PolicyChunk).where(PolicyChunk.policy_id == policy_id)).all())
