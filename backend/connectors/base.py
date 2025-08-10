from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


class ConnectorUnavailable(Exception):
    def __init__(self, provider: str, reason: str) -> None:
        super().__init__(f"{provider} UNAVAILABLE: {reason}")
        self.provider = provider
        self.reason = reason


@dataclass
class LLMConnector:
    id: str
    label: str
    provider: str
    capabilities: Dict[str, bool]

    async def generate(self, prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
        raise NotImplementedError