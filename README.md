# MindForge Brainstormer 2.0 / mindforge-brainstormer

A multi-LLM brainstorming app with Anti-Chaos defaults. Monorepo with FastAPI backend and SvelteKit frontend.

## Stack
- Backend: FastAPI (Python), SQLite via SQLAlchemy, optional Google OAuth (Authlib)
- Frontend: SvelteKit (TypeScript), Tailwind optional, Mermaid via CDN
- Packaging: backend/requirements.txt, frontend/package.json

## Run (One click on Replit or locally)

```bash
bash scripts/start.sh
```
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Frontend proxies `/api/*` to backend

## Environment Variables
Set via Replit Secrets or local env:
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GEMINI_API_KEY
- PERPLEXITY_API_KEY
- GOOGLE_CLIENT_ID (optional)
- GOOGLE_CLIENT_SECRET (optional)
- OAUTH_REDIRECT_URI (optional)

No secrets are exposed to the browser. `/api/test-keys` returns only boolean readiness.

## Data & Exports
- SQLite database at `backend/data/app.db`
- Exports written under `data/exports/<project>/` relative to repo root

## Acceptance Criteria Checklist
- Create/list/rename projects
- Add LLM connectors, per-phase toggles
- Run Expand → Critique → Synthesis with Anti‑Chaos
- Views: Summary, Ideas, Critiques, Mindmap, Kanban
- Export: Markdown, JSON, Mermaid (.mmd), CSV (actions)
- Google Login optional, demo fallback

## Swap to Postgres Later
- Replace SQLite URL in `backend/db.py`

## Add a new connector
- Implement `backend/connectors/<provider>_adapter.py` subclassing `LLMConnector`
- Register provider key in `registry.py`
- Ensure env key check and structured UNAVAILABLE error
