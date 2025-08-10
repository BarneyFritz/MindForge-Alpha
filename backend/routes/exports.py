from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

from ..services.exporters import export_markdown, export_json, export_mermaid, export_csv_actions

router = APIRouter()


class ExportBody(BaseModel):
    projectName: str
    session: dict
    formats: List[str]


@router.post("/export")
def do_export(body: ExportBody):
    paths = []
    if "md" in body.formats:
        p = export_markdown(body.projectName, body.session)
        paths.append(p)
    if "json" in body.formats:
        p = export_json(body.projectName, body.session)
        paths.append(p)
    if "mmd" in body.formats and body.session.get("mermaid"):
        p = export_mermaid(body.projectName, body.session["mermaid"])
        paths.append(p)
    if "csv" in body.formats and body.session.get("summary", {}).get("markdown"):
        p = export_csv_actions(body.projectName, body.session["summary"]["markdown"])
        paths.append(p)
    return {"paths": paths}