from typing import List, Dict
from fastapi import APIRouter
from pydantic import BaseModel

from ..services.exporters import export_markdown, export_json, export_mermaid, export_actions_csv

router = APIRouter()


class ExportBody(BaseModel):
    project: str
    formats: List[str]
    payload: Dict


@router.post("/export")
def export(body: ExportBody):
    paths = []
    if "md" in body.formats:
        paths.append(export_markdown(body.project, body.payload))
    if "json" in body.formats:
        paths.append(export_json(body.project, body.payload))
    if "mmd" in body.formats and body.payload.get("mermaid"):
        paths.append(export_mermaid(body.project, body.payload["mermaid"]))
    if "csv" in body.formats and body.payload.get("summary", {}).get("markdown"):
        paths.append(export_actions_csv(body.project, body.payload["summary"]["markdown"]))
    return {"paths": paths}