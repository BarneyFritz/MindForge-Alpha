from dataclasses import dataclass
from typing import Dict


class ConnectorUnavailable(Exception):
    def __init__(self, provider: str, message: str = "UNAVAILABLE"):
        super().__init__(message)
        self.provider = provider
        self.message = message


@dataclass
class LLMConnector:
    id: str
    label: str
    provider: str
    capabilities: Dict[str, bool]

    async def generate(self, prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
        raise NotImplementedError