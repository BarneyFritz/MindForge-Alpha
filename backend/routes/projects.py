from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from ..db import SessionLocal
from ..models import Project

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str


class ProjectPatch(BaseModel):
    name: Optional[str] = None
    persistent_memory: Optional[bool] = None


@router.post("/projects")
def create_project(body: ProjectCreate):
    db = SessionLocal()
    try:
        project = Project(name=body.name)
        db.add(project)
        db.commit()
        db.refresh(project)
        return {"id": project.id, "name": project.name, "persistent_memory": project.persistent_memory}
    finally:
        db.close()


@router.get("/projects")
def list_projects():
    db = SessionLocal()
    try:
        projects = db.execute(select(Project)).scalars().all()
        return [
            {"id": p.id, "name": p.name, "persistent_memory": p.persistent_memory}
            for p in projects
        ]
    finally:
        db.close()


@router.patch("/projects/{project_id}")
def patch_project(project_id: int, body: ProjectPatch):
    db = SessionLocal()
    try:
        project = db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if body.name is not None:
            project.name = body.name
        if body.persistent_memory is not None:
            project.persistent_memory = body.persistent_memory
        db.commit()
        db.refresh(project)
        return {"id": project.id, "name": project.name, "persistent_memory": project.persistent_memory}
    finally:
        db.close()