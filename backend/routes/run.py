from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.orchestrator import run_pipeline

router = APIRouter()


class RunModels(BaseModel):
    expand: List[int] = []
    critique: List[int] = []
    synth: int | None = None


class RunBody(BaseModel):
    projectId: int
    seed: str
    context: str | None = None
    models: RunModels
    persist: bool = False


@router.post("/run")
async def run(body: RunBody, db: Session = Depends(get_db)) -> Dict[str, Any]:
    payload = await run_pipeline(
        db=db,
        project_id=body.projectId,
        seed=body.seed,
        context=body.context,
        models=body.models.model_dump(),
        persist=body.persist,
    )
    return payload