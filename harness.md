# Speed2Audit - Development Harness & Architecture Blueprint

> **Notice for AGY / Gemini CLI:** This document defines the execution harness, macro-phases, and constraints for building the Speed2Audit Open Core project. Refer to this file to guide architectural decisions step-by-step. Do NOT enforce third-party libraries (e.g., ORMs, UI frameworks, HTTP clients) without discussing trade-offs with the developer first.

---

## Project Core Context
- **Name:** Speed2Audit (`hugonotnice/speed2audit`)
- **Objective:** Open Core mystery shopper & auditing tool for text (and future voice) support channels.
- **Agent Framework:** `google-adk` (Google Agent Development Kit in Python).
- **Execution Model:** Local-First (runs on user infrastructure, local web dashboard, user-provided `GEMINI_API_KEY`).
- **License:** AGPLv3.

---

## Macro-Phase Roadmap

### Macro-Phase 1: Foundation & Scope Freeze (Current Phase)
**Goal:** Establish repository hygiene, open-core boundaries, and minimum execution contract.

* **Invariants (Fixed Decisions):**
  - AGPLv3 License file.
  - Core agent orchestrator powered by `google-adk`.
  - Python 3.11+ environment with strict `.env` credential management.
  - Direct target contact input (manual target configuration; no automated web scraping/browser driving in v1).
* **Open Architectural Decisions (To be decided with AGY in terminal):**
  - **Data Validation & Models:** Evaluate Python standard `dataclasses` vs `msgspec` vs `Pydantic`.
  - **Local UI Framework:** Evaluate `FastHTML` vs `NiceGUI` vs `Gradio` for the simplest, most modern local dashboard.
  - **HTTP/Networking Client:** Evaluate `httpx` vs `aiohttp` vs standard async solutions for messaging adapters.

---

### Macro-Phase 2: Core Engine & ADK Agent Implementation
**Goal:** Implement the mystery shopper logic, prompt persona, and evaluation metrics.

* **Phase 2.1 - Agent Persona & ADK Setup:**
  - Define the `google-adk` Agent with a human-like mystery shopper persona tailored for text channels.
  - Store prompt templates in editable local config files (`.json` or `.yaml`).
* **Phase 2.2 - ADK Tools & Execution:**
  - Build custom `google-adk` Tools for sending messages, receiving responses, and logging quote times.
  - Define deterministic metric calculations: First Response Time (FRT), stage latencies, and quote speed.
* **Phase 2.3 - Stop Condition & Storage:**
  - Implement execution limits (e.g., maximum interaction turns or quote received event).
  - Persist audit session logs to a lightweight local database chosen in Macro-Phase 1.

---

### Macro-Phase 3: Local Dashboard & Developer Experience (DX)
**Goal:** Provide a visual, single-command user experience for running audits and viewing reports.

* **Phase 3.1 - Local Web Dashboard:**
  - Build a lightweight UI to trigger new audits, view active chats, and inspect diagnostic reports.
* **Phase 3.2 - Packaging & DX:**
  - Provide a clean `Dockerfile` and `docker-compose.yml` for multi-stage, containerized runs.
  - Ensure single-command start (e.g., `python -m speed2audit` or Docker startup).

---

### Macro-Phase 4: Go-To-Market & Cloud On-Ramp
**Goal:** Launch on GitHub, drive community adoption, and route enterprise leads to the Cloud waitlist.

* **Phase 4.1 - Repository Showcase:**
  - High-converting `README.md` with visual demo/GIF, AGPLv3 badge, and 1-line quickstart.
* **Phase 4.2 - Public Launch:**
  - Launch announcement posts on Hacker News (*Show HN*), `r/selfhosted`, `r/Python`, and `r/SaaS`.
* **Phase 4.3 - Cloud Conversion:**
  - Landing page capturing hosted/cloud waitlist leads for non-technical users.

---

## Instructions for AGY / Gemini CLI
1. Before proposing code for any Macro-Phase, verify which phase is currently active.
2. Present architectural options with pros and cons before introducing new external dependencies.
3. Prioritize lightweight, modern Python libraries with zero or minimal bloat.
