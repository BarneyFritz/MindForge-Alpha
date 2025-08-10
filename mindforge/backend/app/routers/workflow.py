from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.services.workflow_service import WorkflowOrchestrator, AntiChaosConfig
from app.connectors.base import LLMConfig

router = APIRouter(prefix="/workflow", tags=["workflow"])

class WorkflowInput(BaseModel):
    prompt: str
    llms: List[LLMConfig]
    anti_chaos: AntiChaosConfig | None = None

@router.post("/execute")
async def execute_workflow(payload: WorkflowInput):
    orchestrator = WorkflowOrchestrator(payload.anti_chaos)
    result = await orchestrator.execute_workflow(prompt=payload.prompt, llm_settings=payload.llms)
    return result.model_dump()