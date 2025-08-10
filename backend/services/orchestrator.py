import asyncio
from typing import Dict, List

from sqlalchemy import select

from ..db import SessionLocal
from ..models import Model
from ..prompts import CRITIQUE_PROMPT, SYNTHESIS_PROMPT, ANTI_CHAOS, cap_words
from ..connectors.registry import load_connectors
from ..connectors.base import ConnectorUnavailable


def _model_ref(model: Model) -> str:
    return f"{model.provider}:{model.model_id}"


async def _call(connector, prompt: str, model: Model) -> str:
    temp = (model.temperature or 7) / 10.0
    return await connector.generate(
        prompt=prompt, model_id=model.model_id, temperature=temp, max_tokens=model.max_tokens or 800
    )


async def run_pipeline(project_id: int, seed: str, context: str, model_ids: Dict[str, List[int]], persist: bool) -> Dict:
    db = SessionLocal()
    try:
        # Load models
        id_to_model: Dict[int, Model] = {
            m.id: m for m in db.execute(select(Model)).scalars().all()
        }
        expand_models = [id_to_model[i] for i in model_ids.get("expand", []) if i in id_to_model and id_to_model[i].enable_expand]
        critique_models = [id_to_model[i] for i in model_ids.get("critique", []) if i in id_to_model and id_to_model[i].enable_critique]
        synth_model = id_to_model.get(model_ids.get("synth"))

        connectors = load_connectors()

        # Expand fan-out
        expand_prompt = cap_words(
            f"Seed: {seed}\nContext: {context or ''}\n\nExpand with concrete, non-redundant ideas.",
            ANTI_CHAOS["maxWords"]["expand"],
        )

        ideas: List[Dict] = []

        async def run_expand(m: Model):
            connector = connectors.get(m.provider)
            if not connector:
                return None
            try:
                text = await _call(connector, expand_prompt, m)
                return {"id": None, "modelRef": _model_ref(m), "text": text}
            except ConnectorUnavailable:
                return {"id": None, "modelRef": _model_ref(m), "text": "[UNAVAILABLE]"}

        expand_results = await asyncio.gather(*(run_expand(m) for m in expand_models))
        for idx, r in enumerate([x for x in expand_results if x]):
            r["id"] = idx + 1
            ideas.append(r)

        # Critique round-robin, skipping self-critique
        critiques: List[Dict] = []
        if critique_models and ideas:
            async def critique_one(idea_idx: int, idea: Dict, critic: Model):
                if _model_ref(critic) == idea["modelRef"]:
                    return None
                connector = connectors.get(critic.provider)
                if not connector:
                    return None
                prompt = f"Idea: {idea['text']}\n\n{CRITIQUE_PROMPT}"
                prompt = cap_words(prompt, ANTI_CHAOS["maxWords"]["critique"])
                try:
                    text = await _call(connector, prompt, critic)
                    return {"ideaId": idea["id"], "criticRef": _model_ref(critic), "text": text}
                except ConnectorUnavailable:
                    return None

            tasks = []
            for i, idea in enumerate(ideas):
                critic = critique_models[i % len(critique_models)]
                tasks.append(critique_one(i, idea, critic))
            critique_results = await asyncio.gather(*tasks)
            critiques = [c for c in critique_results if c]

        # Synthesis
        summary = {"modelRef": None, "markdown": ""}
        if synth_model:
            connector = connectors.get(synth_model.provider)
            if connector:
                joined = "\n\n".join([f"Idea {i['id']}: {i['text']}" for i in ideas])
                joined_critiques = "\n".join([f"Idea {c['ideaId']} by {c['criticRef']}: {c['text']}" for c in critiques])
                prompt = (
                    f"Seed: {seed}\nContext: {context or ''}\n\nIdeas:\n{joined}\n\nCritiques:\n{joined_critiques}\n\n{SYNTHESIS_PROMPT}"
                )
                prompt = cap_words(prompt, ANTI_CHAOS["maxWords"]["synth"])  # cap overall words used
                try:
                    md = await _call(connector, prompt, synth_model)
                except ConnectorUnavailable:
                    md = "[SYNTHESIS UNAVAILABLE]"
                summary = {"modelRef": _model_ref(synth_model), "markdown": md}

        return {
            "projectId": project_id,
            "persist": bool(persist),
            "modelsUsed": {
                "expand": [_model_ref(m) for m in expand_models],
                "critique": [_model_ref(m) for m in critique_models],
                "synth": _model_ref(synth_model) if synth_model else None,
            },
            "ideas": ideas,
            "critiques": critiques,
            "summary": summary,
            "antiChaos": ANTI_CHAOS,
        }
    finally:
        db.close()