# MindForge Enterprise Multi-AI Orchestrator

MindForge is a multi-AI brainstorming and synthesis platform with an unlimited LLM plugin system and an Anti-Chaos workflow engine. Built with FastAPI, React, and Tailwind.

## Tech Stack
- Backend: Python 3.11+ (FastAPI, SQLAlchemy Async)
- Frontend: React 18 + TypeScript + Tailwind + Vite
- Database: SQLite (dev) → PostgreSQL (prod)
- Auth: Google OAuth 2.0 + JWT
- Cache: Redis (optional)

## Monorepo Structure
```
mindforge/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quickstart

### Backend
1. Create `.env` from `.env.example` and fill secrets.
2. Install deps:
   ```bash
   python3 -m pip install -r backend/requirements.txt
   ```
3. Run API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend
1. Install deps:
   ```bash
   cd frontend && npm install
   ```
2. Run dev server:
   ```bash
   npm run dev
   ```

## Environment Variables
Copy `.env.example` to `.env` and set values.

## Features
- Unlimited LLM connectors via plugin architecture
- Anti-Chaos workflow to reduce noise and synthesize consensus
- Visualization: Mind Map, Kanban, Metrics
- Universal export to coding platforms

## Deployment
- Railway.app or Docker Compose

## License
Proprietary. All rights reserved.