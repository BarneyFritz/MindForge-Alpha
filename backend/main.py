import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .db import init_db, SessionLocal
from .routes import projects as projects_routes
from .routes import models as models_routes
from .routes import run as run_routes
from .routes import exports as exports_routes
from .routes import auth as auth_routes
from .routes import health as health_routes

from .models import Model

APP_ORIGINS = [
    "http://localhost:5173",
    os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
]

app = FastAPI(title="MindForge Brainstormer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set([o for o in APP_ORIGINS if o])),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", os.urandom(32).hex()),
    session_cookie="mf_session",
    https_only=False,
)

# Routers under /api
app.include_router(health_routes.router, prefix="/api")
app.include_router(projects_routes.router, prefix="/api")
app.include_router(models_routes.router, prefix="/api")
app.include_router(run_routes.router, prefix="/api")
app.include_router(exports_routes.router, prefix="/api")
app.include_router(auth_routes.router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    # Seed example connectors if none exist
    db = SessionLocal()
    try:
        count = db.query(Model).count()
        if count == 0:
            examples = [
                dict(name="OpenAI Default", provider="openai", model_id="gpt-4o-mini", temperature=0.7, max_tokens=1000,
                     enable_expand=True, enable_critique=True, enable_synth=True),
                dict(name="Anthropic Default", provider="anthropic", model_id="claude-3-5-sonnet-latest", temperature=0.7, max_tokens=1000,
                     enable_expand=True, enable_critique=True, enable_synth=True),
                dict(name="Gemini Default", provider="gemini", model_id="gemini-1.5-pro", temperature=0.7, max_tokens=1000,
                     enable_expand=True, enable_critique=True, enable_synth=True),
                dict(name="Perplexity Default", provider="perplexity", model_id="sonar-small-chat", temperature=0.7, max_tokens=1000,
                     enable_expand=True, enable_critique=True, enable_synth=True),
            ]
            for ex in examples:
                m = Model(**ex)
                db.add(m)
            db.commit()
    finally:
        db.close()