from typing import Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from ..services.orchestrator import run_pipeline
from ..services.mermaid import build_mindmap

router = APIRouter()


class RunBody(BaseModel):
    projectId: int
    seed: str
    context: Optional[str] = None
    models: Dict[str, List[int]]
    persist: bool = False


@router.post("/run")
async def run(body: RunBody):
    result = await run_pipeline(
        project_id=body.projectId,
        seed=body.seed,
        context=body.context or "",
        model_ids=body.models,
        persist=body.persist,
    )
    mermaid = build_mindmap(result["ideas"], result["critiques"])
    result["mermaid"] = mermaid
    return result