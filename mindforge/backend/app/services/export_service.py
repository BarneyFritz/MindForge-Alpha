from pydantic import BaseModel
from typing import Dict

class ExportConfig(BaseModel):
    format: str | None = None

class ExportResult(BaseModel):
    format: str
    content: str
    filename: str

class SynthesisResult(BaseModel):
    id: str
    text: str

class BaseExporter:
    def export(self, synthesis: SynthesisResult, config: ExportConfig) -> ExportResult:
        raise NotImplementedError

class BoltExporter(BaseExporter):
    def export(self, synthesis: SynthesisResult, config: ExportConfig) -> ExportResult:
        content = f"# Bolt Prompt\n\n{synthesis.text}\n"
        return ExportResult(format="bolt_prompt", content=content, filename=f"bolt_prompt_{synthesis.id}.md")

class CursorExporter(BaseExporter):
    def export(self, synthesis: SynthesisResult, config: ExportConfig) -> ExportResult:
        content = f"// Cursor Prompt\n{synthesis.text}\n"
        return ExportResult(format="cursor_prompt", content=content, filename=f"cursor_prompt_{synthesis.id}.md")

class ClaudeExporter(BaseExporter):
    def export(self, synthesis: SynthesisResult, config: ExportConfig) -> ExportResult:
        content = f"// Claude Prompt\n{synthesis.text}\n"
        return ExportResult(format="claude_prompt", content=content, filename=f"claude_prompt_{synthesis.id}.md")

class ReplitExporter(BaseExporter):
    def export(self, synthesis: SynthesisResult, config: ExportConfig) -> ExportResult:
        content = f"// Replit Prompt\n{synthesis.text}\n"
        return ExportResult(format="replit_prompt", content=content, filename=f"replit_prompt_{synthesis.id}.md")

class V0Exporter(BaseExporter):
    def export(self, synthesis: SynthesisResult, config: ExportConfig) -> ExportResult:
        content = f"// V0 Prompt\n{synthesis.text}\n"
        return ExportResult(format="v0_prompt", content=content, filename=f"v0_prompt_{synthesis.id}.md")

class CustomExporter(BaseExporter):
    def export(self, synthesis: SynthesisResult, config: ExportConfig) -> ExportResult:
        content = synthesis.text
        return ExportResult(format=config.format or "custom", content=content, filename=f"custom_{synthesis.id}.txt")

class UniversalExporter:
    def __init__(self):
        self.exporters: Dict[str, BaseExporter] = {
            "replit": ReplitExporter(),
            "cursor": CursorExporter(),
            "bolt": BoltExporter(),
            "v0": V0Exporter(),
            "claude": ClaudeExporter(),
            "custom": CustomExporter(),
        }

    def export_to_platform(self, platform: str, synthesis: SynthesisResult, format_config: ExportConfig) -> ExportResult:
        exporter = self.exporters.get(platform)
        if not exporter:
            raise ValueError(f"Unsupported platform: {platform}")
        return exporter.export(synthesis, format_config)