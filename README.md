# MindForge Perplexity — Alpha V1

MindForge is a multi‑AI brainstorming and workflow orchestrator for planning a legal evidence organisation platform.

## Tech Stack
- Backend: FastAPI (Python)
- Frontend: SvelteKit (Vite)
- Database: SQLite via SQLAlchemy ORM (upgrade‑ready for PostgreSQL)
- Auth: Google OAuth (Authlib)
- LLM Connectors: Plugin system with BaseLLMConnector, and built‑in OpenAI, Anthropic (Claude), and Google (Gemini)

## Features
- Secure backend‑only API key storage (.env)
- Projects with persistent memory toggle
- Parallel brainstorming with user‑selected LLMs
- Automated cross‑critique (max 2 rounds, no self‑critique)
- Executive summary by lead LLM
- UI with List, Mindmap, Kanban views; progress bar; round counter; consensus/confidence; summary‑first expandable format
- Export to Markdown, JSON, and Mermaid mindmap (.mmd); stub for GitHub Issue export

## Monorepo Layout
```
backend/
  app/
    main.py
    config.py
    database.py
    models.py
    schemas.py
    orchestrator.py
    auth.py
    connectors/
      base.py
      openai_connector.py
      anthropic_connector.py
      gemini_connector.py
    routers/
      auth.py
      projects.py
      brainstorm.py
      export.py
  alembic/
  .env.example
frontend/
  (SvelteKit app)
```

## Quickstart

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set values for SECRET_KEY, GOOGLE_CLIENT_ID/SECRET, and any LLM keys as needed
uvicorn app.main:app --reload
```

Backend will run at http://localhost:8000

### 2) Frontend

```bash
cd frontend
npm install
npm run dev -- --open
```

Frontend will run at http://localhost:5173

### 3) Environment / Config
- Database URL (default): `sqlite:///./mindforge.db`
- To use PostgreSQL, set `DATABASE_URL=postgresql+psycopg2://user:pass@host:port/dbname`

### 4) Google OAuth
- Set OAuth consent screen and credentials for a web app.
- Authorized redirect URI: `http://localhost:8000/auth/callback`
- Frontend calls backend for login (`/auth/login`) and logout (`/auth/logout`).

### 5) LLM Connectors
- Add keys only to backend `.env`:
  - `OPENAI_API_KEY`
  - `ANTHROPIC_API_KEY`
  - `GOOGLE_API_KEY` (for Gemini)

Connectors auto‑discover available models. If a key is missing, connector will return deterministic stubbed output for development.

### 6) Exports
- Markdown: `/export/session/{session_id}/markdown`
- JSON: `/export/session/{session_id}/json`
- Mermaid Mindmap: `/export/session/{session_id}/mindmap`
- GitHub Issues (stub): `/export/session/{session_id}/github` (no network call; returns payload preview)

### 7) Migrations (Alembic)
- Initial DB is created automatically. For schema changes:
```bash
alembic init alembic
# configure alembic.ini and backend/app/database.py target_metadata
alembic revision -m "description"
alembic upgrade head
```

### 8) Deployment
- Backend: Docker or any ASGI host (Uvicorn/Gunicorn). Set environment variables. Use HTTPS and secure cookie settings.
- Frontend: Static hosting (Vercel/Netlify) or Docker; configure `VITE_API_BASE_URL` to backend origin.

## Post‑Build QA
- Validate project creation, memory toggle, LLM selection, parallel brainstorming, cross‑critique, and summary.
- Check UI responsiveness, error messages, and export endpoints.
- Ensure API keys never flow to frontend (inspect network calls and code).

## License
Proprietary — internal prototype for Personal Legal Intelligence Platform.
