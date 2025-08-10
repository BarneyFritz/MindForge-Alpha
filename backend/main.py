import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from .db import init_db
from .routes import projects as projects_routes
from .routes import models as models_routes
from .routes import run as run_routes
from .routes import exports as exports_routes
from .routes import auth as auth_routes
from .routes import health as health_routes

app = FastAPI(title="MindForge Brainstormer 2.0 API")

origins = [
    "http://localhost:5173",
    os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sessions for optional OAuth
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-me")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

app.include_router(health_routes.router, prefix="/api")
app.include_router(projects_routes.router, prefix="/api")
app.include_router(models_routes.router, prefix="/api")
app.include_router(run_routes.router, prefix="/api")
app.include_router(exports_routes.router, prefix="/api")
app.include_router(auth_routes.router, prefix="/api")


@app.on_event("startup")
async def on_startup() -> None:
    init_db()


@app.get("/api/test-keys")
def test_keys() -> JSONResponse:
    return JSONResponse(
        {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "perplexity": bool(os.getenv("PERPLEXITY_API_KEY")),
            "google_oauth": bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET")),
        }
    )