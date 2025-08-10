from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.services.connector_service import registry
from app.connectors.base import LLMConfig

router = APIRouter(prefix="/connectors", tags=["connectors"])

@router.get("/available")
async def list_connectors() -> Dict[str, Any]:
    return {"connectors": registry.list_available_connectors()}

class TestConfig(BaseModel):
    name: str
    api_url: str = ""
    headers: Dict[str, str] = {}
    model_name: str | None = None

@router.post("/test")
async def test_connector(cfg: TestConfig):
    connector = registry.get_connector(cfg.name, LLMConfig(**cfg.model_dump()))
    return await connector.test_connection()