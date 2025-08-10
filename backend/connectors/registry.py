from typing import Dict, List
from sqlalchemy.orm import Session

from ..models import ModelConfig
from .base import LLMConnector, ConnectorUnavailable
from .openai_adapter import OpenAIConnector
from .anthropic_adapter import AnthropicConnector
from .gemini_adapter import GeminiConnector
from .perplexity_adapter import PerplexityConnector


def load_connectors(db: Session, model_ids: List[int]) -> Dict[int, LLMConnector]:
    connectors: Dict[int, LLMConnector] = {}
    rows = db.query(ModelConfig).filter(ModelConfig.id.in_(model_ids)).all()
    for row in rows:
        try:
            capabilities = {
                "expand": bool(row.enable_expand),
                "critique": bool(row.enable_critique),
                "synth": bool(row.enable_synth),
            }
            if row.provider == "openai":
                connectors[row.id] = OpenAIConnector(id=str(row.id), label=row.name, capabilities=capabilities)
            elif row.provider == "anthropic":
                connectors[row.id] = AnthropicConnector(id=str(row.id), label=row.name, capabilities=capabilities)
            elif row.provider == "gemini":
                connectors[row.id] = GeminiConnector(id=str(row.id), label=row.name, capabilities=capabilities)
            elif row.provider == "perplexity":
                connectors[row.id] = PerplexityConnector(id=str(row.id), label=row.name, capabilities=capabilities)
        except ConnectorUnavailable:
            # Skip unavailable connectors; orchestrator will surface warnings
            continue
    return connectors