from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Project
from ..schemas import ProjectCreate, ProjectOut
from ..auth import get_user_from_session

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectOut])
async def list_projects(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    rows = db.query(Project).filter(Project.owner_id == user["id"]).order_by(Project.created_at.desc()).all()
    return rows

@router.post("/", response_model=ProjectOut)
async def create_project(payload: ProjectCreate, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    proj = Project(owner_id=user["id"], name=payload.name, description=payload.description, persistent_memory=payload.persistent_memory)
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj