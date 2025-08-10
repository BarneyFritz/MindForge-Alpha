from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .config import get_settings
from .database import Base, engine
from .routers import auth as auth_router
from .routers import projects as projects_router
from .routers import brainstorm as brainstorm_router
from .routers import export as export_router
# Import connectors to trigger registry registration
from .connectors import openai_connector, anthropic_connector, gemini_connector

settings = get_settings()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MindForge Perplexity — Alpha V1")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(auth_router.router)
app.include_router(projects_router.router)
app.include_router(brainstorm_router.router)
app.include_router(export_router.router)

@app.get("/")
async def root():
    return {"name": "MindForge Perplexity — Alpha V1"}