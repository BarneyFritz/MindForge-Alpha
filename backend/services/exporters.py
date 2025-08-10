import os
import json
from datetime import datetime
from typing import Dict, List

EXPORT_BASE = "/workspace/data/exports"


def ensure_dir(project_name: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    target = os.path.join(EXPORT_BASE, project_name)
    os.makedirs(target, exist_ok=True)
    return target, ts


def export_markdown(project_name: str, payload: Dict) -> str:
    target, ts = ensure_dir(project_name)
    md = ["# MindForge Session\n"]
    if payload.get("summary", {}).get("markdown"):
        md.append(payload["summary"]["markdown"] + "\n")
    md.append("\n## Ideas\n")
    for i in payload.get("ideas", []):
        md.append(f"- ({i['modelRef']}) {i['text']}")
    md.append("\n## Critiques\n")
    for c in payload.get("critiques", []):
        md.append(f"- idea {c['ideaId']} by {c['criticRef']}: {c['text']}")
    content = "\n".join(md)
    path = os.path.join(target, f"{ts}-session.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def export_json(project_name: str, payload: Dict) -> str:
    target, ts = ensure_dir(project_name)
    path = os.path.join(target, f"{ts}-session.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path


def export_mermaid(project_name: str, mermaid_str: str) -> str:
    target, ts = ensure_dir(project_name)
    path = os.path.join(target, f"{ts}-mindmap.mmd")
    with open(path, "w", encoding="utf-8") as f:
        f.write(mermaid_str)
    return path


def export_csv_actions(project_name: str, summary_markdown: str) -> str:
    target, ts = ensure_dir(project_name)
    # Naive extraction: lines starting with "-" under "Next Actions"
    lines = []
    capture = False
    for line in summary_markdown.splitlines():
        if "Next Actions" in line:
            capture = True
            continue
        if capture and line.strip().startswith("-"):
            text = line.strip().lstrip("- ")
            lines.append(text)
        elif capture and line.strip() and not line.strip().startswith("-"):
            break
    path = os.path.join(target, f"{ts}-actions.csv")
    with open(path, "w", encoding="utf-8") as f:
        f.write("Action\n")
        for l in lines:
            f.write(f'"{l.replace("\"", "''")}"\n')
    return path