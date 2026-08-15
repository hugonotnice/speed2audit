# Speed2Audit - Development Harness & Architecture Blueprint

> **Notice for AGY / Gemini CLI / Aider / Developers:** This document defines the execution harness, macro-phases, and finalized architectural decisions for Speed2Audit. Detailed functional specifications are in `PRD.md`.

---

## Project Core Context
- **Name:** Speed2Audit (`hugonotnice/speed2audit`)
- **Objective:** Open Core mystery shopper & auditing platform for WhatsApp (and future voice) customer service and sales channels.
- **Detailed Specification:** See `PRD.md` at project root.
- **Agent Framework:** `LangGraph` + `langchain-google-genai` (Google Gemini 2.5 Flash).
- **Conversational Cockpit UI:** `Chainlit` (Human-in-the-Loop, Live Chat Mirror, Inline Markdown Report Export).
- **WhatsApp Channel Gateway:** `WAHA` (WhatsApp HTTP API in Docker) consumed via `httpx` and Inbound Webhook parser.
- **Observability:** `Arize Phoenix` (Local-first OpenTelemetry on `http://localhost:6006`) + `LangGraph Studio` (`langgraph dev`) + `LangSmith`.
- **Storage / Persistence:** `SQLite` (`speed2audit.db`).
- **Execution Model:** Local-First (runs on user machine, user-provided `GEMINI_API_KEY`).
- **License:** AGPLv3.

---

## Spec-Driven Development (Governance)
- **Aider Architect Mode:** O desenvolvimento e a escrita de código devem ser estritamente conduzidos pelo **Aider** no modo `--architect`.
- **Fonte Absoluta da Verdade (Read-Only Specs):** A IA nunca deve codificar "no escuro". Os arquivos `PRD.md`, `harness.md` e `GEMINI.md` são a fonte absoluta da verdade e devem ser passados como arquivos de leitura (`--read`) para o Aider.
- **Validação Automatizada por Testes:** Nenhuma funcionalidade ou módulo deve ser considerado concluído sem passar no comando de teste automatizado:
  ```bash
  uv run pytest
  ```

---

## Current Status & Macro-Phase Roadmap

### ✅ Macro-Phase 1: Foundation & Scope Freeze (COMPLETED)
- Git repository hygiene, AGPLv3 license, `.gitignore`.
- Full specification documented in `PRD.md` and `harness.md`.
- Environment managed via `uv` with Python 3.13.

### ✅ Macro-Phase 2: Core Multi-Agent Engine & WAHA Integration (COMPLETED)
- **Phase 2.1:** Pydantic models (`PersonaProfile`, `ConversationTurn`, `Scorecard`, `AuditSession`) and SQLite database persistence.
- **Phase 2.2:** `ContextScraper` (BeautifulSoup4 + httpx) and `PersonaGenerator` (Gemini 2.5 Flash structured output).
- **Phase 2.3:** `WAHAClient` (session management, typing simulation, message dispatch with 15–40s human delay) and `ShopperAgent`.
- **Phase 2.4:** `AuditorAgent` with FRT latency calculation and LLM-as-a-judge scorecards (0–10).
- **Phase 2.5:** `LangGraph` state graph (`AuditState` with `scrape_node`, `persona_node`, `shopper_node`, `auditor_node`).

### ✅ Macro-Phase 3: Conversational Cockpit & Developer Experience (COMPLETED)
- **Phase 3.1:** Module A (`HealthChecker`) validating WAHA Docker and Gemini API key.
- **Phase 3.2:** Module B (`Chainlit` Cockpit app in `src/speed2audit/app.py`):
  - URL input $\rightarrow$ Persona generation $\rightarrow$ HITL approval $\rightarrow$ WhatsApp number input $\rightarrow$ Live audit mirror with pause/stop action.
- **Phase 3.3:** Inline Audit Report Exporter (`reports/audit_report_<session_id>.md`) directly downloaded in Cockpit.
- **Phase 3.4:** WAHA Inbound Webhook Parser (`src/speed2audit/channels/webhook.py`).
- **Phase 3.5:** Observability & Dev Tools:
  - Local Arize Phoenix integration on `http://localhost:6006`.
  - LangGraph Studio configuration (`langgraph.json` + `langgraph-cli[inmem]` + `langgraph-api 0.12.4`).
  - LLM upgraded to `gemini-2.5-flash`.
- **Test Suite Status:** 27 unit/integration tests passing in ~1.0s.

---

### ⏳ Macro-Phase 4: Live Usability Testing & Packaging (NEXT UP)

**O que fazer assim que retomar a sessão:**
1. **Teste Visual de Grafo (LangGraph Studio):**
   ```bash
   uv run langgraph dev
   ```
2. **Teste de Ponta a Ponta no Cockpit (Chainlit):**
   - Subir o WAHA: `docker run -d --name waha -p 3000:3000 devlikeapro/waha`
   - Escanear o QR Code em `http://localhost:3000/dashboard`
   - Subir o Cockpit: `uv run chainlit run src/speed2audit/app.py -w`
   - Realizar uma auditoria ao vivo contra um WhatsApp de teste.
3. **Packaging (`docker-compose.yml`):**
   - Criar `docker-compose.yml` para orquestrar Speed2Audit + WAHA com 1 comando.
