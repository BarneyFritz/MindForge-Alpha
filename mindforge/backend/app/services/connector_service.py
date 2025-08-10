from typing import Dict, List, Type
from app.connectors.base import BaseLLMConnector, LLMConfig
from app.connectors.openai_connector import OpenAIConnector
from app.connectors.anthropic_connector import AnthropicConnector
from app.connectors.google_connector import GoogleConnector
from app.connectors.ollama_connector import OllamaConnector
from app.connectors.custom_connector import CustomConnector

class ConnectorRegistry:
    def __init__(self):
        self._connectors: Dict[str, Type[BaseLLMConnector]] = {}
        self._discover_connectors()

    def register_connector(self, name: str, connector_class: Type[BaseLLMConnector]):
        self._connectors[name] = connector_class

    def get_connector(self, name: str, config: LLMConfig) -> BaseLLMConnector:
        if name not in self._connectors:
            raise ValueError(f"Connector {name} not found")
        return self._connectors[name](config)

    def list_available_connectors(self) -> List[str]:
        return list(self._connectors.keys())

    def _discover_connectors(self):
        self.register_connector("openai", OpenAIConnector)
        self.register_connector("anthropic", AnthropicConnector)
        self.register_connector("google", GoogleConnector)
        self.register_connector("ollama", OllamaConnector)
        self.register_connector("custom", CustomConnector)

registry = ConnectorRegistry()