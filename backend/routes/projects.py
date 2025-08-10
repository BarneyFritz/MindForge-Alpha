from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..db import get_db
from ..models import Project

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str


class ProjectUpdate(BaseModel):
    name: str | None = None
    persistent_memory: bool | None = None


@router.post("/projects")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    proj = Project(name=payload.name)
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return {"id": proj.id, "name": proj.name, "persistent_memory": proj.persistent_memory}


@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    items = db.query(Project).order_by(Project.created_at.desc()).all()
    return [
        {"id": p.id, "name": p.name, "persistent_memory": p.persistent_memory}
        for p in items
    ]


@router.patch("/projects/{project_id}")
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        return JSONResponse({"error": "Not found"}, status_code=404)
    if payload.name is not None:
        proj.name = payload.name
    if payload.persistent_memory is not None:
        proj.persistent_memory = payload.persistent_memory
    db.commit()
    return {"id": proj.id, "name": proj.name, "persistent_memory": proj.persistent_memory}