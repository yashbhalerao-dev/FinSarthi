# Architecture (Phase 0)

FinSarthi is a hybrid retrieval and eligibility system. Retrieval finds policy evidence. Structured Python rules evaluate explicit conditions. An LLM may explain those results using retrieved evidence; it is not the eligibility authority.

```
Next.js Frontend
        ↓
FastAPI API / Orchestrator
        ↓
Profile / Document / Policy / Retrieval / Eligibility / Evidence
        ↓
OCR + LangChain + Pinecone + Python Rules
        ↓
Evidence-grounded result
```

Status: **Phase 0 foundation**. Health check and frontend shell exist. Profile, document, policy, retrieval, eligibility, and generation services are not implemented yet.

Ingestion of verified official sources stays separate from the user-facing application (`data/` and later `scripts/ingest_policies.py`).
