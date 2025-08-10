import os
import json
from datetime import datetime
from typing import Dict, List

EXPORT_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "exports")
os.makedirs(EXPORT_ROOT, exist_ok=True)


def ensure_project_dir(project_name: str) -> str:
    safe = project_name.replace("/", "-").replace(" ", "_")
    path = os.path.join(EXPORT_ROOT, safe)
    os.makedirs(path, exist_ok=True)
    return path


def export_markdown(project: str, payload: Dict) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(ensure_project_dir(project), f"{ts}-session.md")
    summary = payload.get("summary", {}).get("markdown", "")
    lines = ["# Summary", "", summary, "", "# Ideas"]
    for idea in payload.get("ideas", []):
        lines.append(f"\n## {idea['modelRef']}")
        lines.append(idea["text"])
    lines.append("\n# Critiques")
    for crit in payload.get("critiques", []):
        lines.append(f"\n## Idea {crit['ideaId']} by {crit['criticRef']}")
        lines.append(crit["text"]) 
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def export_json(project: str, payload: Dict) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(ensure_project_dir(project), f"{ts}-session.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def export_mermaid(project: str, mermaid: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(ensure_project_dir(project), f"{ts}-mindmap.mmd")
    with open(path, "w", encoding="utf-8") as f:
        f.write(mermaid)
    return path


def export_actions_csv(project: str, summary_md: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(ensure_project_dir(project), f"{ts}-actions.csv")
    # naive extract: lines under "Next Actions"
    lines = ["Title,Description"]
    capture = False
    for line in summary_md.splitlines():
        if "Next Actions" in line:
            capture = True
            continue
        if capture:
            if line.startswith("-") or line.startswith("*") or line.strip().startswith("1."):
                item = line.lstrip("-* 1234567890.\t").strip().replace(",", ";")
                lines.append(f"{item[:40]},{item}")
            elif line.strip() == "":
                break
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path