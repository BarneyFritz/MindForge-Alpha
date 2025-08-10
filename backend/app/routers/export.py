from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import BrainstormSession, Message
from ..schemas import ExportPayload
from ..auth import get_user_from_session

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/session/{session_id}/markdown", response_class=PlainTextResponse)
async def export_markdown(session_id: int, request: Request, db: Session = Depends(get_db)):
    session_obj = _get_owned_session(session_id, request, db)
    msgs = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    md = _to_markdown(session_obj, msgs)
    return md

@router.get("/session/{session_id}/json", response_class=JSONResponse)
async def export_json(session_id: int, request: Request, db: Session = Depends(get_db)):
    session_obj = _get_owned_session(session_id, request, db)
    msgs = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    data = {
        "session": {
            "id": session_obj.id,
            "project_id": session_obj.project_id,
            "prompt": session_obj.prompt,
            "connectors": session_obj.selected_connectors,
            "rounds": session_obj.rounds,
            "lead": session_obj.lead_connector,
            "status": session_obj.status,
        },
        "messages": [
            {
                "id": m.id,
                "connector": m.connector,
                "role": m.role,
                "round": m.round_index,
                "content": m.content,
                "model": m.model_used,
                "confidence": m.confidence,
            } for m in msgs
        ]
    }
    return data

@router.get("/session/{session_id}/mindmap", response_class=PlainTextResponse)
async def export_mindmap(session_id: int, request: Request, db: Session = Depends(get_db)):
    session_obj = _get_owned_session(session_id, request, db)
    msgs = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    mmd = _to_mermaid_mindmap(session_obj, msgs)
    return mmd

@router.post("/session/{session_id}/github", response_model=ExportPayload)
async def export_github_stub(session_id: int, request: Request, db: Session = Depends(get_db)):
    session_obj = _get_owned_session(session_id, request, db)
    msgs = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    payload = ExportPayload(
        session_id=session_id,
        markdown=_to_markdown(session_obj, msgs),
        json={"title": f"Brainstorm: {session_obj.prompt[:50]}", "body": _to_markdown(session_obj, msgs)},
        mindmap=_to_mermaid_mindmap(session_obj, msgs),
    )
    return payload


def _get_owned_session(session_id: int, request: Request, db: Session) -> BrainstormSession:
    user = get_user_from_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    session_obj = db.query(BrainstormSession).get(session_id)
    if not session_obj or session_obj.project.owner_id != user["id"]:
        raise HTTPException(status_code=404, detail="Not found")
    return session_obj


def _to_markdown(session_obj: BrainstormSession, msgs: List[Message]) -> str:
    lines = [
        f"# Brainstorm Session {session_obj.id}",
        f"Prompt: {session_obj.prompt}",
        f"Connectors: {', '.join(session_obj.selected_connectors)}",
        f"Rounds: {session_obj.rounds}",
        "",
        "## Ideas",
    ]
    for m in msgs:
        if m.role == "idea":
            lines.append(f"- [{m.connector}] {m.content}")
    lines.append("\n## Critiques")
    for m in msgs:
        if m.role == "critique":
            lines.append(f"- [{m.connector}] {m.content}")
    lines.append("\n## Executive Summary")
    for m in msgs:
        if m.role == "summary":
            lines.append(m.content)
            break
    return "\n".join(lines)


def _to_mermaid_mindmap(session_obj: BrainstormSession, msgs: List[Message]) -> str:
    lines = ["mindmap", f"  root(({session_obj.prompt[:60]}...))"]
    for m in msgs:
        if m.role == "idea":
            lines.append(f"    {m.connector}({m.connector})")
            first_line = m.content.splitlines()[0][:80]
            lines.append(f"      {m.connector}_idea({first_line})")
    for m in msgs:
        if m.role == "critique":
            first_line = m.content.splitlines()[0][:80]
            lines.append(f"      {m.connector}_crit({first_line})")
    for m in msgs:
        if m.role == "summary":
            first_line = m.content.splitlines()[0][:80]
            lines.append(f"    summary({first_line})")
            break
    return "\n".join(lines)