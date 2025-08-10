from __future__ import annotations
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

class BaseLLMConnector(ABC):
    name: str = "base"
    default_model: str = "default"

    def __init__(self, api_key_env: str | None = None):
        self.api_key = os.environ.get(api_key_env) if api_key_env else None

    @abstractmethod
    async def generate(self, prompt: str) -> dict:
        ...

    @abstractmethod
    async def critique(self, prompt: str, peers: Dict[str, str]) -> dict:
        ...

    async def summarize(self, prompt: str, ideas: Dict[str, str], critiques: Dict[str, str]) -> dict:
        # Default summarization combines ideas and critiques succinctly.
        combined = []
        for name, idea in ideas.items():
            critique = critiques.get(name, "")
            combined.append(f"[{name}] Idea: {idea}\n[{name}] Critique: {critique}")
        return {
            "text": ("\n".join(combined))[:4000],
            "model": self.default_model,
            "confidence": 0.5,
        }

class ConnectorRegistry:
    _registry: Dict[str, Type[BaseLLMConnector]] = {}

    @classmethod
    def register(cls, connector_cls: Type[BaseLLMConnector]):
        cls._registry[connector_cls.name] = connector_cls
        return connector_cls

    @classmethod
    def create(cls, name: str) -> BaseLLMConnector:
        if name not in cls._registry:
            raise ValueError(f"Unknown connector: {name}")
        connector_cls = cls._registry[name]
        return connector_cls()

    @classmethod
    def available_connectors(cls) -> List[str]:
        return list(cls._registry.keys())