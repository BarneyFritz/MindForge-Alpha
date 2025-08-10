from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from ..db import SessionLocal
from ..models import Model

router = APIRouter()


class ModelCreate(BaseModel):
    name: str
    provider: str
    model_id: str
    temperature: float = 0.7
    max_tokens: int = 1000
    enable_expand: bool = True
    enable_critique: bool = True
    enable_synth: bool = True


@router.post("/models")
def add_model(body: ModelCreate):
    db = SessionLocal()
    try:
        # store temperature as tenths
        m = Model(
            name=body.name,
            provider=body.provider,
            model_id=body.model_id,
            temperature=int(body.temperature * 10),
            max_tokens=body.max_tokens,
            enable_expand=body.enable_expand,
            enable_critique=body.enable_critique,
            enable_synth=body.enable_synth,
        )
        db.add(m)
        db.commit()
        db.refresh(m)
        return _to_dict(m)
    finally:
        db.close()


@router.get("/models")
def list_models():
    db = SessionLocal()
    try:
        models = db.execute(select(Model)).scalars().all()
        return [_to_dict(m) for m in models]
    finally:
        db.close()


def _to_dict(m: Model):
    return {
        "id": m.id,
        "name": m.name,
        "provider": m.provider,
        "model_id": m.model_id,
        "temperature": m.temperature / 10.0,
        "max_tokens": m.max_tokens,
        "enable_expand": m.enable_expand,
        "enable_critique": m.enable_critique,
        "enable_synth": m.enable_synth,
    }