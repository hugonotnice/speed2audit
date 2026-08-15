# Contributing to Speed2Audit

Thank you for your interest in contributing to **Speed2Audit**! We welcome community contributions to build the most robust, local-first mystery shopper and conversational auditing platform.

---

## 🛠️ Development Setup

1. **Prerequisites:**
   - Python `3.12+` or `3.13`
   - [`uv`](https://github.com/astral-sh/uv) (Extremely fast Python package manager)
   - Docker (for running WAHA WhatsApp Gateway locally)

2. **Clone the repository:**
   ```bash
   git clone https://github.com/hugonotnice/speed2audit.git
   cd speed2audit
   ```

3. **Install dependencies:**
   ```bash
   uv sync --all-groups
   ```

4. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY to .env
   ```

---

## 🧪 Testing & Code Quality

Before opening a pull request, ensure all checks pass:

1. **Run Linter & Format Check (Ruff):**
   ```bash
   uv run ruff check
   uv run ruff format --check
   ```
   To automatically fix formatting issues:
   ```bash
   uv run ruff check --fix && uv run ruff format
   ```

2. **Run Test Suite (pytest):**
   ```bash
   uv run pytest
   ```

---

## 📐 Architecture & Principles

- **Local-First & Privacy:** Audits run locally on user-controlled infrastructure. No telemetry or conversational logs are sent to third parties without explicit user consent.
- **Spec-Driven Governance:** Check [`PRD.md`](./PRD.md) and [`harness.md`](./harness.md) before designing new features.
- **Conventional Commits:** Please use structured commit messages (e.g., `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`).

---

## ⚖️ License
By contributing to Speed2Audit, you agree that your contributions will be licensed under the **GNU Affero General Public License v3 (AGPLv3)**.
