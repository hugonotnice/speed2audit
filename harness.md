# Speed2Audit - Development Harness & Architecture Blueprint

> **Notice for AGY / Gemini CLI:** This document defines the execution harness, macro-phases, and finalized architectural decisions for building Speed2Audit. Detailed functional specifications are in `PRD.md`.

---

## Project Core Context
- **Name:** Speed2Audit (`hugonotnice/speed2audit`)
- **Objective:** Open Core mystery shopper & auditing platform for WhatsApp (and future voice) customer service channels.
- **Detailed Specification:** See `PRD.md` at project root.
- **Agent Framework:** `LangGraph` + `langchain-google-genai` (Google Gemini 2.0 Flash).
- **Conversational Cockpit UI:** `Chainlit` (Human-in-the-Loop & Live Streaming).
- **WhatsApp Channel Gateway:** `WAHA` (WhatsApp HTTP API in Docker) consumed via `httpx`.
- **Observability:** `Arize Phoenix` (Local OpenTelemetry tracing).
- **Storage / Persistence:** `SQLite` (`speed2audit.db`).
- **Execution Model:** Local-First (runs on user infrastructure, local web dashboard, user-provided `GEMINI_API_KEY`).
- **License:** AGPLv3.

---

## Macro-Phase Roadmap

### Macro-Phase 1: Foundation & Scope Freeze (Completed)
**Goal:** Establish repository hygiene, architectural boundaries, and product requirements specification (`PRD.md`).

* **Invariants (Finalized Decisions):**
  - Python 3.12+ environment managed with `uv`.
  - Multi-agent topology: Scraper Agent $\rightarrow$ Persona Generator Agent $\rightarrow$ Shopper Agent $\rightarrow$ Auditor Agent.
  - Conversational Cockpit built with `Chainlit` with Human-in-the-Loop approval for personas and live chat steering.
  - WAHA-backed WhatsApp messaging with fixed 15–40s human delay + typing simulation.
  - Local persistence via SQLite.

---

### Macro-Phase 2: Core Multi-Agent Engine & WAHA Integration
**Goal:** Implement data models, WAHA client, and the 4 specialized agents in LangGraph.

* **Phase 2.1 - Core Models & Storage:**
  - Define Pydantic models (`PersonaProfile`, `ConversationTurn`, `Scorecard`, `AuditSession`).
  - Initialize SQLite persistence layer.
* **Phase 2.2 - Scraper & Persona Generator:**
  - Build website crawling agent to extract business context and ICP.
  - Build Persona generator with dynamic prompt templating.
* **Phase 2.3 - Shopper Agent & WAHA Client:**
  - Build asynchronous `WAHAClient` via `httpx` (send text, simulate typing presence, poll/receive inbound messages).
  - Implement fixed 15–40s random human delay before message dispatch.
* **Phase 2.4 - Auditor & Evaluator Agent:**
  - LLM-as-a-judge prompt for calculating Speed to Lead (FRT), communication clarity, objection handling, and scorecard generation.

---

### Macro-Phase 3: Conversational Cockpit (Chainlit) & Módulos A, B, C
**Goal:** Deliver the interactive web experience.

* **Phase 3.1 - Módulo A (Health Check):**
  - Auto-verification of WAHA container, QR Code state, and `GEMINI_API_KEY` on startup.
* **Phase 3.2 - Módulo B (O Cockpit):**
  - Chainlit onboarding flow: URL input $\rightarrow$ Persona generation $\rightarrow$ HITL approval $\rightarrow$ WhatsApp number input $\rightarrow$ Live audit mirror with user intervention.
* **Phase 3.3 - Módulo C (Audit Reports & History):**
  - Dedicated screen to filter past sessions and inspect detailed scorecards and annotated transcripts.

---

### Macro-Phase 4: Packaging & Launch
**Goal:** Containerization, documentation, and open-core release.

* **Phase 4.1 - Docker & DX:**
  - `docker-compose.yml` orchestrating Speed2Audit + WAHA container in 1 command.
* **Phase 4.2 - Public Showcase:**
  - Visual README with GIF demo, quickstart guide, and AGPLv3 badge.
