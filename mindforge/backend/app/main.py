from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.config import get_settings
from app.routers import auth as auth_router
from app.routers import connectors as connectors_router
from app.routers import workflow as workflow_router
from app.utils.db import engine, Base

settings = get_settings()

app = FastAPI(title="MindForge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

app.include_router(auth_router.router)
app.include_router(connectors_router.router)
app.include_router(workflow_router.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def on_shutdown():
    pass