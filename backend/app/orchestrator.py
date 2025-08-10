from __future__ import annotations
import asyncio
from typing import Dict, List
from sqlalchemy.orm import Session
from .models import BrainstormSession, Message
from .connectors.base import ConnectorRegistry, BaseLLMConnector
from .database import SessionLocal

async def _safe_call(coro, fallback_text: str) -> dict:
    try:
        return await coro
    except Exception:
        return {"text": fallback_text, "model": "stub", "confidence": 0.4}

async def run_brainstorm(db: Session, session_obj: BrainstormSession) -> None:
    # Kept for potential direct calling in-process; prefer run_brainstorm_by_id for background tasks
    await _execute_brainstorm(db, session_obj)

async def run_brainstorm_by_id(session_id: int) -> None:
    db = SessionLocal()
    try:
        session_obj = db.query(BrainstormSession).get(session_id)
        if not session_obj:
            return
        await _execute_brainstorm(db, session_obj)
    finally:
        db.close()

async def _execute_brainstorm(db: Session, session_obj: BrainstormSession) -> None:
    session_obj.status = "running"
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)

    connectors: Dict[str, BaseLLMConnector] = {}
    for name in session_obj.selected_connectors:
        connectors[name] = ConnectorRegistry.create(name)

    # Round 0: ideas in parallel
    idea_tasks = []
    for name, connector in connectors.items():
        idea_tasks.append(_safe_call(connector.generate(session_obj.prompt), f"[{name}] idea (stub)"))
    idea_results = await asyncio.gather(*idea_tasks)
    name_list = list(connectors.keys())
    ideas: Dict[str, str] = {name_list[i]: idea_results[i]["text"] for i in range(len(name_list))}

    for i, name in enumerate(name_list):
        db.add(Message(
            session_id=session_obj.id,
            connector=name,
            role="idea",
            round_index=0,
            content=ideas[name],
            model_used=idea_results[i].get("model"),
            confidence=idea_results[i].get("confidence"),
        ))
    db.commit()

    # Critique rounds (max 2, no self-critique)
    max_rounds = min(max(session_obj.rounds, 0), 2)
    critiques_accum: Dict[str, str] = {}

    for round_idx in range(1, max_rounds + 1):
        critique_tasks = []
        critique_targets: List[str] = []
        for name, connector in connectors.items():
            peer_ideas = {k: v for k, v in ideas.items() if k != name}
            critique_tasks.append(_safe_call(connector.critique(session_obj.prompt, peer_ideas), f"[{name}] critique (stub)"))
            critique_targets.append(name)
        critique_results = await asyncio.gather(*critique_tasks)
        for j, name in enumerate(critique_targets):
            text = critique_results[j]["text"]
            db.add(Message(
                session_id=session_obj.id,
                connector=name,
                role="critique",
                round_index=round_idx,
                content=text,
                model_used=critique_results[j].get("model"),
                confidence=critique_results[j].get("confidence"),
            ))
            # Keep the most recent critique per connector for summary
            critiques_accum[name] = text
        db.commit()

    # Executive summary by lead LLM
    name_list = list(connectors.keys())
    lead_name = session_obj.lead_connector if session_obj.lead_connector in connectors else (name_list[0] if name_list else "openai")
    if lead_name in connectors:
        lead = connectors[lead_name]
        summary = await _safe_call(lead.summarize(session_obj.prompt, ideas, critiques_accum), f"[{lead_name}] summary (stub)")
        db.add(Message(
            session_id=session_obj.id,
            connector=lead_name,
            role="summary",
            round_index=max_rounds + 1,
            content=summary["text"],
            model_used=summary.get("model"),
            confidence=summary.get("confidence"),
        ))

    session_obj.status = "complete"
    db.add(session_obj)
    db.commit()