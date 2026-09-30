"""Ingest the synthetic demo policy corpus: chunk, metadata, local embeddings, optional Pinecone."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from sqlmodel import Session, select

from ai.rag.chunker import chunk_policy_text
from ai.rag.embeddings import embedding_id_for, get_embedding_provider
from app.core.config import get_settings
from app.core.db import engine, init_db
from app.models.entities import Policy, PolicyChunk
from app.services.policy_service import upsert_policies


def attach_local_embeddings(session: Session) -> int:
    provider = get_embedding_provider()
    updated = 0
    for chunk in session.exec(select(PolicyChunk)).all():
        chunk.embedding_id = embedding_id_for(chunk.text)
        meta = dict(chunk.metadata_json or {})
        meta["embedding_provider"] = provider.provider_id
        chunk.metadata_json = meta
        session.add(chunk)
        updated += 1
    session.commit()
    return updated


def maybe_upsert_pinecone(session: Session) -> int:
    settings = get_settings()
    if not settings.pinecone_enabled:
        return 0
    try:
        from pinecone import Pinecone  # type: ignore
    except Exception:
        print("Pinecone package not installed; skipping remote upsert.")
        return 0
    provider = get_embedding_provider()
    client = Pinecone(api_key=settings.pinecone_api_key)
    index = client.Index(settings.pinecone_index)
    vectors = []
    policies = {policy.id: policy for policy in session.exec(select(Policy)).all()}
    for chunk in session.exec(select(PolicyChunk)).all():
        policy = policies.get(chunk.policy_id)
        if policy is None:
            continue
        vectors.append(
            {
                "id": chunk.embedding_id or chunk.id,
                "values": provider.embed_query(chunk.text),
                "metadata": {
                    "policy_id": chunk.policy_id,
                    "chunk_id": chunk.id,
                    "text": chunk.text,
                    "section": chunk.section,
                    "page_reference": chunk.page_reference,
                    "source_url": policy.source_url,
                    "jurisdiction": policy.jurisdiction,
                    "applicant_type": policy.applicant_type,
                },
            }
        )
    if vectors:
        index.upsert(vectors=vectors)
    return len(vectors)


def ingest_raw_text_files(session: Session) -> int:
    raw_dir = ROOT / "data" / "raw"
    added = 0
    if not raw_dir.exists():
        return 0
    for path in raw_dir.glob("*.txt"):
        policy_id = f"synthetic-raw-{path.stem}"
        existing = session.get(Policy, policy_id)
        if existing:
            continue
        payload = chunk_policy_text(policy_id, path.read_text(encoding="utf-8"))
        policy = Policy(
            id=policy_id,
            name=f"SYNTHETIC DEMO ingested file {path.name} (not a government scheme)",
            issuing_authority="FinSarthi Synthetic Demo Authority",
            jurisdiction="unknown",
            category="ingested_demo",
            applicant_type="any",
            source_url=f"synthetic://demo/raw/{path.name}",
            source_document=path.name,
            status="synthetic_demo",
            synthetic=True,
            conditions=[],
            required_documents=[],
            benefit={"supported_by_source": False, "amount": None},
            application_route={"url": "synthetic://demo/apply/raw", "steps": []},
        )
        session.add(policy)
        for chunk in payload["chunks"]:
            session.add(
                PolicyChunk(
                    id=chunk["id"],
                    policy_id=policy_id,
                    text=chunk["text"],
                    section=chunk.get("section"),
                    page_reference=chunk.get("page_reference"),
                    metadata_json=chunk.get("metadata") or {},
                )
            )
            added += 1
        session.commit()
    return added


def main() -> None:
    init_db()
    with Session(engine) as session:
        upsert_policies(session)
        raw_chunks = ingest_raw_text_files(session)
        embedded = attach_local_embeddings(session)
        pinecone_count = maybe_upsert_pinecone(session)
        print(f"ingested corpus; raw_chunks={raw_chunks}; embeddings={embedded}; pinecone_upserts={pinecone_count}")


if __name__ == "__main__":
    main()
