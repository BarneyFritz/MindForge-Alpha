from __future__ import annotations
import asyncio
from typing import Dict
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import BrainstormSession, Message, Project
from ..schemas import SessionCreate, SessionOut, MessageOut
from ..auth import get_user_from_session
from ..orchestrator import run_brainstorm_by_id, _execute_brainstorm

router = APIRouter(prefix="/brainstorm", tags=["brainstorm"])

@router.post("/sessions", response_model=SessionOut)
async def create_session(payload: SessionCreate, background: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    project = db.query(Project).filter(Project.id == payload.project_id, Project.owner_id == user["id"]).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session_obj = BrainstormSession(
        project_id=project.id,
        prompt=payload.prompt,
        selected_connectors=payload.selected_connectors,
        rounds=min(max(payload.rounds, 0), 2),
        lead_connector=payload.lead_connector,
        status="pending",
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    # Fire-and-forget task on the running event loop
    asyncio.create_task(run_brainstorm_by_id(session_obj.id))
    return _session_to_out(db, session_obj)

@router.post("/sessions/{session_id}/run-now", response_model=SessionOut)
async def run_now(session_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    session_obj = db.query(BrainstormSession).get(session_id)
    if not session_obj or session_obj.project.owner_id != user["id"]:
        raise HTTPException(status_code=404, detail="Not found")
    await _execute_brainstorm(db, session_obj)
    db.refresh(session_obj)
    return _session_to_out(db, session_obj)

@router.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session(session_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    session_obj = db.query(BrainstormSession).get(session_id)
    if not session_obj or session_obj.project.owner_id != user["id"]:
        raise HTTPException(status_code=404, detail="Not found")
    return _session_to_out(db, session_obj)

@router.get("/sessions/{session_id}/messages", response_model=list[MessageOut])
async def get_messages(session_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    session_obj = db.query(BrainstormSession).get(session_id)
    if not session_obj or session_obj.project.owner_id != user["id"]:
        raise HTTPException(status_code=404, detail="Not found")
    msgs = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    return msgs


def _session_to_out(db: Session, s: BrainstormSession) -> SessionOut:
    msgs = db.query(Message).filter(Message.session_id == s.id).order_by(Message.created_at.asc()).all()
    return SessionOut(
        id=s.id,
        project_id=s.project_id,
        prompt=s.prompt,
        selected_connectors=s.selected_connectors,
        rounds=s.rounds,
        lead_connector=s.lead_connector,
        status=s.status,
        created_at=s.created_at,
        updated_at=s.updated_at,
        messages=msgs,
    )