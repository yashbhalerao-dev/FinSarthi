💰 FIN-03 — Financial Policy Discovery, Eligibility & Application Assistant

«An Agentic AI-powered assistant that discovers government financial schemes, verifies eligibility, estimates benefits, and guides applicants through the application process.»

""Theme" (https://img.shields.io/badge/Theme-Agentic%20AI-purple)"
""Problem Statement" (https://img.shields.io/badge/FIN--03-Financial%20Policy%20Assistant-blue)"
""AI" (https://img.shields.io/badge/AI-Agentic%20AI-orange)"
""RAG" (https://img.shields.io/badge/Architecture-RAG-green)"
""Status" (https://img.shields.io/badge/Status-In%20Development-yellow)"

---

🌟 Overview

Government subsidies, tax benefits, grants, and financial assistance programs can provide significant support to individuals and small businesses. However, discovering the right scheme, understanding its eligibility criteria, collecting the required documents, and completing the application process can be difficult.

Information is often scattered across government portals, policy documents, PDFs, notifications, and different departmental websites.

Our solution

Financial Policy Discovery, Eligibility & Application Assistant is an Agentic AI system that acts as an intelligent financial-policy assistant.

It analyzes applicant information and documents, discovers relevant government schemes, verifies eligibility against official rules, estimates potential benefits, identifies missing documents, and provides step-by-step application guidance.

Instead of simply generating an AI response, the system uses specialized agents, verified policy sources, deterministic eligibility rules, and human-in-the-loop verification to produce transparent and trustworthy results.

---

🎯 Problem Statement

People and small businesses frequently miss out on government financial benefits because:

- Government schemes are difficult to discover.
- Eligibility criteria can be complicated.
- Information is distributed across multiple sources.
- Official guidelines are often lengthy PDF documents.
- Applicants may not know which documents are required.
- Benefit calculations can be difficult.
- Different schemes have different conditions.
- Borderline cases can be difficult to interpret.
- AI-generated answers without sources can be unreliable.

The goal

«Turn complex government policy information into a personalized, explainable, and actionable application assistant.»

---

🤖 Why Agentic AI?

This project is designed around the principles of Agentic AI.

Instead of a simple:

User → Chatbot → Answer

our system follows an autonomous workflow:

                         👤 USER
                            │
                            ▼
                 ┌────────────────────┐
                 │  Supervisor Agent  │
                 └─────────┬──────────┘
                           │
          ┌────────────────┼─────────────────┐
          ▼                ▼                 ▼
   📄 Document        🔎 Research       ⚖️ Eligibility
      Agent              Agent              Agent
          │                │                 │
          ▼                ▼                 ▼
       OCR +          Policy/RAG       Rule Engine
      Extraction        Search
          │                │                 │
          └────────────────┼─────────────────┘
                           ▼
                  💰 Benefit Agent
                           │
                           ▼
                📋 Application Agent
                           │
                           ▼
                ┌────────────────────┐
                │  Decision Engine   │
                └─────────┬──────────┘
                          │
               ┌──────────┴──────────┐
               ▼                     ▼
          ✅ Clear Result       ⚠️ Unclear Case
               │                     │
               ▼                     ▼
        Applicant Guidance     👨‍💼 Human Review

The agents can:

- Understand applicant goals
- Extract information from documents
- Identify missing information
- Search relevant policies
- Retrieve official scheme documents
- Analyze eligibility requirements
- Calculate potential benefits
- Identify missing documents
- Generate application instructions
- Detect ambiguous cases
- Escalate uncertain decisions to humans

---

🧠 Core Features

1. 📄 Intelligent Document Extraction

Applicants can upload documents such as:

- Income Certificate
- Aadhaar / Identity documents
- Business registration documents
- GST documents
- Bank documents
- Caste/category certificates
- Land/property documents
- Other supporting documents

The system extracts relevant information and converts it into structured applicant data.

Example:

{
  "age": 24,
  "state": "Maharashtra",
  "occupation": "Small Business",
  "annual_income": 210000,
  "business_type": "MSME"
}

---

2. 🔎 AI-Powered Scheme Discovery

The Research Agent searches the scheme knowledge base and retrieves potentially relevant government schemes.

It considers applicant characteristics such as:

- Age
- Location
- Income
- Occupation
- Business type
- Category
- Business turnover
- Land ownership
- Other scheme-specific criteria

---

3. ⚖️ Verified Eligibility Checking

The system does not rely solely on LLM reasoning for eligibility.

Eligibility conditions are evaluated using a rule-based decision engine.

Example:

Annual Income ≤ ₹3,00,000       ✅
Age ≥ 18                         ✅
State = Maharashtra              ✅
Business Type = MSME             ✅

Result → ELIGIBLE

Each condition is evaluated individually.

---

4. 📊 Transparent Eligibility Explanation

Instead of simply saying:

«"You are eligible."»

the system explains why.

Example:

✅ ELIGIBLE

Reason:

• Required income: ≤ ₹3,00,000
• Verified income: ₹2,10,000
• Requirement satisfied.

• Required age: ≥ 18
• Verified age: 24
• Requirement satisfied.

---

5. 💰 Benefit Estimation

The system estimates the potential financial benefit based on the scheme rules.

Example:

Estimated Benefit
────────────────────
Up to ₹50,000

Calculation:
Eligible subsidy = 25% of eligible investment
Eligible investment = ₹2,00,000
Estimated subsidy = ₹50,000

«Benefit estimates are presented as estimates and are subject to official scheme rules and approval.»

---

6. 📋 Missing Document Detection

The system compares:

Required Documents
        VS
Uploaded Documents

Example:

Required Documents

✅ Aadhaar
✅ Income Certificate
✅ Business Registration

❌ Bank Statement
⚠️ GST Certificate

The applicant immediately knows what is missing.

---

7. 📚 Source-Backed Decisions

Every eligibility determination should be traceable to an official source.

Example:

Eligibility Rule
──────────────────────────────
Annual income must not exceed
₹3,00,000.

Source
──────────────────────────────
Official Scheme Guidelines

Section
──────────────────────────────
Section 4.2 — Eligibility

Evidence
──────────────────────────────
Applicant's verified income:
₹2,10,000

This provides explainability and traceability instead of unsupported AI answers.

---

⚠️ Human-in-the-Loop

Not every policy situation can be safely resolved automatically.

If information is:

- Missing
- Contradictory
- Ambiguous
- Outside the supported rules
- Difficult to interpret

the system does not force an answer.

Instead:

⚠️ MANUAL REVIEW REQUIRED

The available information is insufficient
to confidently determine eligibility.

Reason:
Business classification could not be
verified from the submitted documents.

This prevents false-confidence decisions.

---

🔄 Complete User Workflow

1. 👤 Applicant enters basic information
                ↓
2. 📄 Uploads supporting documents
                ↓
3. 🤖 Document Agent extracts information
                ↓
4. 🔎 Research Agent finds relevant schemes
                ↓
5. 📚 Retrieves official policy documents
                ↓
6. ⚖️ Eligibility Engine checks every rule
                ↓
7. 💰 Benefit Agent estimates potential benefits
                ↓
8. 📋 Missing-document checker runs
                ↓
9. 🧠 Supervisor Agent combines results
                ↓
10. 📊 Personalized results are displayed
                ↓
11. 📝 Application steps are generated
                ↓
12. ⚠️ Unclear cases → Human Review

---

🏗️ System Architecture

┌─────────────────────────────────────────────────────┐
│                    USER INTERFACE                   │
│              Web Dashboard / Assistant              │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                 SUPERVISOR AGENT                    │
│          Planning • Orchestration • Routing         │
└───────────┬─────────────┬─────────────┬─────────────┘
            │             │             │
            ▼             ▼             ▼
      Document Agent  Research Agent  Eligibility Agent
            │             │             │
            ▼             ▼             ▼
          OCR          RAG/Search     Rule Engine
            │             │             │
            └─────────────┼─────────────┘
                          ▼
                  Benefit Calculator
                          │
                          ▼
                 Application Agent
                          │
                          ▼
                Human Review System
                          │
                          ▼
                 Final User Report

---

🧩 Major Components

🧑‍💼 Supervisor Agent

Responsible for:

- Understanding the user's objective
- Planning the workflow
- Calling appropriate tools/agents
- Combining results
- Detecting incomplete information
- Escalating uncertain cases

📄 Document Agent

Responsible for:

- Reading uploaded documents
- OCR
- Information extraction
- Document classification
- Data validation

🔎 Research Agent

Responsible for:

- Finding relevant schemes
- Retrieving policy documents
- Searching the knowledge base
- Identifying applicable rules

⚖️ Eligibility Agent

Responsible for:

- Evaluating eligibility criteria
- Comparing applicant data with rules
- Producing condition-by-condition results
- Identifying borderline cases

💰 Benefit Agent

Responsible for:

- Applying scheme-specific formulas
- Estimating potential benefits
- Explaining calculations

📋 Application Agent

Responsible for:

- Identifying missing documents
- Explaining application steps
- Providing official application links
- Preparing an application checklist

---

🛠️ Technology Stack

Layer| Technology
Frontend| HTML, CSS, JavaScript, Bootstrap
Backend| Python, Django / Django REST Framework
Database| PostgreSQL
AI| LLM
Agent Framework| Agent orchestration framework
RAG| Embeddings + Vector Database
OCR| OCR engine / document parser
Documents| PDF / DOCX / Images
Rule Engine| Python-based deterministic rules
Authentication| Django Authentication
Deployment| Cloud / Containerized deployment

---

📚 Knowledge Base

The knowledge base contains verified government scheme information.

Each scheme can contain:

Scheme Name
├── Government Department
├── Description
├── Target Beneficiaries
├── Eligibility Rules
├── Benefit Formula
├── Required Documents
├── Application Process
├── Official Application Portal
├── Official Guidelines
└── Source / Last Updated

The system prioritizes official government sources for policy decisions.

---

🧪 Testing Strategy

The system is tested using three major categories.

✅ Clearly Eligible

Applicant satisfies all required conditions.

Expected:
→ Eligible
→ Benefit estimate
→ Application guidance

❌ Clearly Ineligible

Applicant fails one or more mandatory conditions.

Expected:
→ Not Eligible
→ Exact failed condition
→ Source rule

⚠️ Borderline / Unclear

Information is incomplete or ambiguous.

Expected:
→ Manual Review
→ Reason for uncertainty
→ Information/document required

This ensures the system does not produce false-confident decisions.

---

🔐 Trust, Safety & Explainability

The system is designed around several principles:

🔹 Source First

Eligibility decisions are backed by official policy documents.

🔹 Rule-Based Verification

Critical eligibility conditions are checked using deterministic rules.

🔹 Explainable Decisions

Users can understand why a scheme matched or failed.

🔹 Human-in-the-Loop

Uncertain cases are escalated instead of guessed.

🔹 Data Minimization

Only information required for scheme evaluation should be processed.

🔹 Clear Disclaimer

The system provides guidance and estimates. Final eligibility and benefit approval remain subject to the relevant government authority and official scheme rules.

---

🎯 Expected Outcomes

The system aims to provide:

- ✅ Relevant government scheme discovery
- ✅ Automated applicant information extraction
- ✅ Verified eligibility matching
- ✅ Explainable eligibility decisions
- ✅ Benefit estimation
- ✅ Missing-document detection
- ✅ Application guidance
- ✅ Official source references
- ✅ Borderline-case detection
- ✅ Human review workflow
- ✅ Agentic task planning and execution

---

🚀 Future Scope

Potential future improvements include:

- 🌐 Support for more states and central schemes
- 🗣️ Multilingual voice assistant
- 📱 Mobile application
- 🔄 Automatic policy-update detection
- 🧾 Advanced document verification
- 🏦 Tax deduction and financial planning modules
- 🔔 Personalized scheme alerts
- 📊 Applicant financial dashboard
- 🧠 More advanced multi-agent collaboration
- 🔗 Integration with official government APIs where available

---

💡 Example Use Case

Scenario

A 24-year-old small-business owner from Maharashtra wants to know what government financial assistance may be available.

Input

Age: 24
State: Maharashtra
Annual Income: ₹2,10,000
Occupation: Small Business
Business Type: MSME

The applicant uploads supporting documents.

Agentic Workflow

Document Agent
      ↓
Extracts applicant information
      ↓
Research Agent
      ↓
Finds relevant schemes
      ↓
Eligibility Agent
      ↓
Checks official eligibility rules
      ↓
Benefit Agent
      ↓
Calculates estimated benefit
      ↓
Application Agent
      ↓
Generates application checklist

Output

🎯 Relevant Scheme Found

Status: ✅ Eligible

Estimated Benefit:
Up to ₹50,000

Eligibility:
✓ Age requirement satisfied
✓ Income requirement satisfied
✓ Location requirement satisfied
✓ Business requirement satisfied

Missing Documents:
❌ Bank Statement

Next Steps:
1. Obtain bank statement
2. Prepare required documents
3. Visit official application portal
4. Submit application

---

🏆 Project Vision

«Make government financial assistance easier to discover, understand, and access — while keeping every important decision transparent, source-backed, and human-verifiable.»

---

👨‍💻 Team

FIN-03 — Financial Policy Discovery, Eligibility & Application Assistant

Built as an Agentic AI solution focused on:

Discover → Verify → Explain → Estimate → Guide → Escalate

---

📌 Disclaimer

This system is intended to assist users in discovering and understanding government financial schemes. Eligibility results and benefit amounts are estimates based on available information and the referenced scheme rules. Final eligibility, approval, and benefit amounts are determined by the respective government authority.