# FinSarthi

Financial Policy Discovery, Eligibility & Application Assistant

Team: NeuroSquad

## Project Overview

FinSarthi helps individuals and small businesses discover relevant government financial policies, understand explicit eligibility conditions, and see what to do next — without treating a language model as the decision maker.

Users can be **Individuals** or **Small Businesses**. They provide profile information and supporting documents. The system then:

- extracts and normalizes relevant attributes
- discovers relevant **verified** financial policies from a controlled corpus
- evaluates **explicit** eligibility conditions with a Python rule engine
- identifies missing documents
- provides source-backed benefit information **only when the policy source supports it**
- shows evidence (citations) and official application routes
- uses **NEEDS_VERIFICATION** when critical information is missing, conflicting, or uncertain

FinSarthi is decision support. Final eligibility, approval, and benefit amounts remain with the concerned government authority.

## Current Status

**50% Functional Prototype — Implementation in Progress**

This repository is at **Phase 0 (repository foundation)**. The product architecture and technology choices are locked so the prototype can grow to 100% without a rewrite. The end-to-end workflow, APIs, OCR/retrieval, policy corpus, and eligibility engine are **not** complete yet.

Do not treat this README as a claim that the full system is working.

## Core Architecture

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

Boundaries stay separate: ingestion, profile intelligence, retrieval, eligibility, and generation. Later work can scale one layer without replacing the product.

**Decision path (locked):**

1. Retrieval finds policy evidence.
2. Python rules evaluate explicit eligibility conditions.
3. The LLM produces a readable, evidence-grounded explanation. It is **not** the authoritative eligibility decision maker.
4. Generation receives retrieved evidence plus structured rule results. Policy facts, thresholds, benefits, and citations are not invented.

## Technology Stack

Locked for this project:

- Next.js
- TypeScript
- Python
- FastAPI
- LangChain
- Pinecone
- Replaceable OCR adapter
- Python eligibility rule engine
- Evidence-grounded LLM
- SQLite-compatible prototype storage
- Git + GitHub

## Key Features

Scope is the **50% prototype** defined in the implementation blueprint. Items below are **planned** unless Phase 0 notes say they already exist.

**Implemented in Phase 0**

- Repository layout for frontend, backend, AI, data, docs, and scripts
- FastAPI health endpoint (`GET /api/health`)
- Next.js landing page and dashboard route shell
- Environment variable template (`.env.example`)

**Planned for the 50% milestone (not claimed as complete)**

- Responsive landing, dashboard, and application workflow
- Profile creation for an individual and a small-business profile
- Document upload for PDF/image inputs
- Document processing endpoint and a replaceable OCR/extraction adapter
- Structured extracted profile with uncertain fields clearly marked
- Controlled verified policy corpus (small number of official sources)
- Policy metadata (name, source, jurisdiction, category, version/effective information where available)
- Retrieval of relevant policy chunks (LangChain + Pinecone)
- Python eligibility engine with three overall states and three condition states
- Missing-document comparison
- Benefit information only when supported by the policy source
- Result screen: eligibility state, reasons, missing documents, evidence/source, application route
- Demo cases: at least one individual, one small business, and one borderline (Needs Verification)
- Automated tests for profile validation and eligibility rules

## User Journey

50% flow (screens and APIs land in later phases):

Landing  
→ Individual / Small Business  
→ Profile  
→ Document Upload  
→ Extraction  
→ Review / Correction  
→ Policy Discovery  
→ Eligibility Evaluation  
→ Missing Documents  
→ Evidence / Benefit  
→ Official Application Route

Result states shown to the user: **Eligible**, **Not Eligible**, or **Needs Verification**.

## Eligibility States

**Overall**

- `ELIGIBLE`
- `NOT_ELIGIBLE`
- `NEEDS_VERIFICATION`

**Condition-level**

- `SATISFIED`
- `NOT_SATISFIED`
- `NEEDS_VERIFICATION`

The **LLM is not the authoritative eligibility decision maker**. Explicit Python rules determine eligibility. If a critical field is missing, unreadable, or conflicting, the system prefers `NEEDS_VERIFICATION` rather than inventing a value. Unsupported benefit amounts are not generated.

## Project Structure

```
FinSarthi/
├── frontend/     # Next.js App Router UI
├── backend/      # FastAPI API and orchestration
├── ai/           # OCR adapter, RAG (LangChain/Pinecone), evidence generation
├── data/         # Raw sources, processed text, scheme records, metadata
├── docs/         # Architecture and later API / data-model / demo-case docs
├── scripts/      # Policy ingest and demo seed (later phases)
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

| Path | Role |
| --- | --- |
| `frontend/` | User-facing workflow. Calls FastAPI. Must not hard-code scheme rules. |
| `backend/` | HTTP API, validation, orchestration, persistence. |
| `ai/` | Replaceable OCR, chunking, embeddings, retrieval, controlled generation. |
| `data/` | Verified corpus and related files. Ingestion stays separate from the app. |
| `docs/` | Architecture and contracts as they are implemented. |
| `scripts/` | Offline ingest and seed utilities. |

Target APIs (not all implemented yet):

- `POST /api/profile`
- `GET /api/profile/{id}`
- `POST /api/documents/upload`
- `POST /api/documents/process`
- `POST /api/policies/search`
- `POST /api/eligibility/evaluate`
- `GET /api/results/{id}`
- `GET /api/health` — **implemented in Phase 0**

## Team

| Member | Ownership |
| --- | --- |
| Yash Bhalerao | Backend, integration, orchestration, QA |
| Vaibhav Khandare | Next.js frontend |
| Poorva Sawant | OCR, extraction, RAG and retrieval |
| Purva Thorat | Verified policy corpus, eligibility rules and tests |

Work is expected on feature branches with pull-request review. See Development Phases for sequence.

## Development Phases

| Phase | Purpose |
| --- | --- |
| 0. Repo foundation | Initialize architecture, env, README, branches. App starts; structure is stable. **Current phase.** |
| 1. Frontend | Complete prototype UX. All screens navigate with realistic state. |
| 2. Backend | Profile, document, and result APIs so the frontend can call the backend. |
| 3. Policy data | Verified demo corpus with metadata and source references. |
| 4. Rules | Eligibility engine and missing-document comparison; known test cases classify correctly. |
| 5. OCR | Extraction adapter and review path so document fields enter the profile pipeline. |
| 6. Retrieval | Pinecone / LangChain retrieval returning relevant evidence with metadata. |
| 7. Integration | Full vertical slice: upload → profile → retrieval → eligibility → result. |
| 8. QA | Clear and borderline cases; expected outputs and traceable citations. |

## 50% Definition of Done

These criteria define the **50% milestone**. They are **not** all met yet.

- A fresh clone can be installed using documented setup instructions.
- The frontend starts and exposes the full prototype journey.
- The backend health endpoint works.
- At least one real (synthetic/redacted demo) document can pass through the processing pipeline.
- Extracted profile fields can be reviewed and edited.
- A controlled policy corpus is available.
- Retrieval returns policy evidence relevant to a test profile.
- The eligibility engine produces all three overall decision states across test cases.
- The result page displays reasons, benefits where source-supported, missing documents, and source evidence.
- At least two end-to-end demo profiles work: one individual and one small business.
- At least one borderline case produces Needs Verification.
- No secrets are committed.
- This README explains architecture, setup, demo cases when they exist, and current limitations.
- All four team members have genuine contributions in their assigned modules.

## Setup (Phase 0)

Copy environment variables. Never commit a real `.env`.

```bash
cp .env.example .env
```

**Backend** (Python 3.12+):

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir .
```

Health check: `GET http://127.0.0.1:8000/api/health` → `{ "status": "ok" }`.

**Frontend** (Node.js 20+):

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. Landing includes a Start control that navigates to the dashboard shell.

## Security & Data Handling

- Use **synthetic or redacted** demo documents for development and presentation. Do not use real personal identity documents unless explicitly authorized and necessary.
- Secrets and API keys belong in environment variables only. Provide `.env.example` without credentials.
- Never commit Pinecone, OCR, LLM, or other API keys.
- Do not store unnecessary personal data (data minimization).
- Document storage is behind an abstraction so encryption, retention, and deletion can be added later.
- FinSarthi is **decision support**. It does not replace authority approval of eligibility or benefits.

## Future Expansion

The 50% build is the first half of the same product, not a throwaway demo.

| 50% foundation | 100% direction (later) |
| --- | --- |
| Controlled policy corpus | Source ingestion, approval, versioning |
| OCR adapter | Additional providers, confidence checks, classification |
| Basic retrieval | Hybrid retrieval, reranking, monitoring |
| Static Python rules | Rule authoring, richer conditions, governance |
| Prototype result flow | Accounts, history, audit, case management |
| Official application route | Guided application assistance |
| SQLite-compatible prototype store | Production storage, security, retention |
| Single-language prototype UX | Localization and accessibility expansion |

Policy data, rules, and services stay modular so the corpus can grow without burying scheme logic in the frontend or in prompts.

## Current Limitations

- The prototype uses a **controlled** (small, manually verified) policy corpus, not national-scale coverage.
- OCR and retrieval may use **adapters or stubs** during early development; they are not production OCR or a finished RAG pipeline in Phase 0.
- Production-scale ingestion, policy governance, user accounts, audit trails, advanced retrieval, localization, and related 100% work are **future phases**.
- No verified scheme names, thresholds, or benefit amounts are published in this repository until they are taken from official sources in the policy-data phase.
- Feature branches and remaining APIs are not part of the Phase 0 runtime.

## License

See [LICENSE](LICENSE).
