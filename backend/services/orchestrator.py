from __future__ import annotations
import asyncio
from typing import Dict, List, Any
from sqlalchemy.orm import Session

from ..models import Session as DbSession, Idea as DbIdea, Critique as DbCritique, Summary as DbSummary, Project as DbProject, ModelConfig
from ..connectors.registry import load_connectors
from ..connectors.base import LLMConnector
from ..prompts import CRITIQUE_PROMPT, SYNTHESIS_PROMPT, ANTI_CHAOS
from .mermaid import build_mindmap


def truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])


async def call_connector(conn: LLMConnector, prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
    return await conn.generate(prompt, model_id, temperature, max_tokens)


async def run_pipeline(
    db: Session,
    project_id: int,
    seed: str,
    context: str | None,
    models: Dict[str, Any],
    persist: bool,
) -> Dict[str, Any]:
    project: DbProject | None = db.query(DbProject).filter(DbProject.id == project_id).first()

    expand_ids: List[int] = models.get("expand", [])
    critique_ids: List[int] = models.get("critique", [])
    synth_id: int | None = models.get("synth")

    connectors_all = load_connectors(db, list(set(expand_ids + critique_ids + ([synth_id] if synth_id else []))))
    unavailable = list(set(expand_ids + critique_ids + ([synth_id] if synth_id else [])) - set(connectors_all.keys()))

    # Step A: Expand
    async def expand_call(mid: int, conn: LLMConnector) -> str:
        cfg = db.get(ModelConfig, mid)
        prompt = seed if not context else f"Context:\n{context}\n\nSeed:\n{seed}\n\nGenerate ideas (<= {ANTI_CHAOS['maxWords']['expand']} words)."
        text = await call_connector(conn, prompt, cfg.model_id, float(cfg.temperature), int(cfg.max_tokens))
        return truncate_words(text.strip(), ANTI_CHAOS["maxWords"]["expand"])

    expand_meta = [(mid, connectors_all.get(mid)) for mid in expand_ids if connectors_all.get(mid)]
    expand_results = await asyncio.gather(*[expand_call(mid, conn) for mid, conn in expand_meta], return_exceptions=True)

    ideas: List[Dict[str, Any]] = []
    for idx, res in enumerate(expand_results):
        mid, conn = expand_meta[idx]
        if isinstance(res, Exception):
            continue
        idea_obj = {"id": idx + 1, "modelRef": f"{conn.provider}:{mid}", "text": res}
        ideas.append(idea_obj)

    # Step B: Critique (round-robin, no self critique)
    critiques: List[Dict[str, Any]] = []
    for idea in ideas:
        for cid in critique_ids:
            cconn = connectors_all.get(cid)
            if not cconn:
                continue
            critic_ref = f"{cconn.provider}:{cid}"
            if critic_ref == idea["modelRef"]:
                continue
            cfg = db.get(ModelConfig, cid)
            prompt = f"Idea:\n{idea['text']}\n\n{CRITIQUE_PROMPT}"
            try:
                text = await call_connector(cconn, prompt, cfg.model_id, float(cfg.temperature), int(cfg.max_tokens))
                text = truncate_words(text.strip(), ANTI_CHAOS["maxWords"]["critique"])
                critiques.append({"ideaId": idea["id"], "criticRef": critic_ref, "text": text})
            except Exception:
                continue

    # Step C: Synthesis
    summary = {"modelRef": None, "markdown": ""}
    if synth_id and synth_id in connectors_all:
        sconn = connectors_all[synth_id]
        cfg = db.get(ModelConfig, synth_id)
        idea_bullets = "\n".join([f"- {i['modelRef']}: {i['text'][:200]}" for i in ideas])
        critique_bullets = "\n".join([f"- {c['criticRef']} on Idea {c['ideaId']}: {c['text'][:160]}" for c in critiques])
        synth_prompt = (
            f"Seed:\n{seed}\n\nContext:\n{context or ''}\n\nIdeas:\n{idea_bullets}\n\nCritiques:\n{critique_bullets}\n\n{SYNTHESIS_PROMPT}"
        )
        try:
            md = await call_connector(sconn, synth_prompt, cfg.model_id, float(cfg.temperature), int(cfg.max_tokens))
            md = truncate_words(md.strip(), ANTI_CHAOS["maxWords"]["synth"])
            summary = {"modelRef": f"{sconn.provider}:{synth_id}", "markdown": md}
        except Exception:
            pass

    mermaid = build_mindmap(seed, ideas, critiques)

    payload = {
        "projectId": project_id,
        "persist": persist,
        "modelsUsed": {
            "expand": [f"{connectors_all[mid].provider}:{mid}" for mid in expand_ids if mid in connectors_all],
            "critique": [f"{connectors_all[mid].provider}:{mid}" for mid in critique_ids if mid in connectors_all],
            "synth": f"{connectors_all[synth_id].provider}:{synth_id}" if synth_id and synth_id in connectors_all else None,
        },
        "ideas": ideas,
        "critiques": critiques,
        "summary": summary,
        "mermaid": mermaid,
        "antiChaos": ANTI_CHAOS,
        "unavailableModels": unavailable,
    }

    if persist:
        db_sess = DbSession(project_id=project_id, seed=seed, context=context or "")
        db.add(db_sess)
        db.commit()
        db.refresh(db_sess)
        for idea in ideas:
            db.add(DbIdea(session_id=db_sess.id, model_ref=idea["modelRef"], text=idea["text"]))
        for crit in critiques:
            db.add(DbCritique(session_id=db_sess.id, idea_id=crit["ideaId"], critic_ref=crit["criticRef"], text=crit["text"]))
        if summary["markdown"]:
            db.add(DbSummary(session_id=db_sess.id, model_ref=summary["modelRef"] or "", markdown=summary["markdown"]))
        db.commit()

    return payload