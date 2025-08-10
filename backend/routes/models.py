from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os

from ..db import get_db
from ..models import ModelConfig

router = APIRouter()


class ModelCreate(BaseModel):
    name: str
    provider: str
    model_id: str
    temperature: float = 1.0
    max_tokens: int = 512
    enable_expand: bool = True
    enable_critique: bool = True
    enable_synth: bool = True


@router.post("/models")
def add_model(payload: ModelCreate, db: Session = Depends(get_db)):
    row = ModelConfig(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row.__dict__ | {"id": row.id}


@router.get("/models")
def list_models(db: Session = Depends(get_db)):
    rows = db.query(ModelConfig).order_by(ModelConfig.created_at.desc()).all()
    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "name": r.name,
            "provider": r.provider,
            "model_id": r.model_id,
            "temperature": r.temperature,
            "max_tokens": r.max_tokens,
            "enable_expand": r.enable_expand,
            "enable_critique": r.enable_critique,
            "enable_synth": r.enable_synth,
        })
    return out


@router.post("/models/seed")
def seed_models(db: Session = Depends(get_db)):
    if db.query(ModelConfig).count() > 0:
        return {"ok": True, "seeded": False}

    examples = [
        ("OpenAI GPT-4o Mini", "openai", "gpt-4o-mini"),
        ("Anthropic Claude 3 Haiku", "anthropic", "claude-3-haiku-20240307"),
        ("Google Gemini 1.5 Flash", "gemini", "gemini-1.5-flash"),
        ("Perplexity Sonar Small", "perplexity", "sonar-small-chat"),
    ]
    for name, provider, model_id in examples:
        enabled = bool(os.getenv(f"{provider.upper()}_API_KEY"))
        row = ModelConfig(
            name=name,
            provider=provider,
            model_id=model_id,
            temperature=0.7,
            max_tokens=512,
            enable_expand=enabled,
            enable_critique=enabled,
            enable_synth=enabled,
        )
        db.add(row)
    db.commit()

    return {"ok": True, "seeded": True}