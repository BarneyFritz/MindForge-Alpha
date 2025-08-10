from typing import List, Dict


def build_mindmap(ideas: List[Dict], critiques: List[Dict]) -> str:
    # Basic: root seed with ideas as children and critics as subnodes
    idea_id_to_critiques = {}
    for c in critiques:
        idea_id_to_critiques.setdefault(c["ideaId"], []).append(c)

    lines = ["mindmap", "  Root"]
    for idea in ideas:
        idea_text = idea["text"].split("\n")[0][:80]
        lines.append(f"    {idea_text}")
        for c in idea_id_to_critiques.get(idea["id"], []):
            critic = c["criticRef"]
            ctext = c["text"].split("\n")[0][:80]
            lines.append(f"      ({critic}) {ctext}")
    return "\n".join(lines)