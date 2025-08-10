from typing import List, Dict


def escape(text: str) -> str:
    return text.replace("\n", " ").replace("|", " ")


def build_mindmap(seed: str, ideas: List[Dict], critiques: List[Dict]) -> str:
    lines = ["mindmap", f"  root(({escape(seed[:80])}))"]
    idea_id_to_label = {}
    for idx, idea in enumerate(ideas, start=1):
        label = f"Idea {idx}: {idea['modelRef']}"
        idea_id_to_label[idea["id"]] = label
        lines.append(f"    {label}:::{'idea'}")
        for line in idea["text"].split("\n"):
            if line.strip():
                lines.append(f"      {escape(line.strip())}")

    for critique in critiques:
        idea_label = idea_id_to_label.get(critique["ideaId"]) or "Idea"
        lines.append(f"    {idea_label} --> Critique by {escape(critique['criticRef'])}")
        for line in critique["text"].split("\n"):
            if line.strip():
                lines.append(f"      {escape(line.strip())}")

    return "\n".join(lines)