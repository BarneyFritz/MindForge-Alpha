from typing import Dict
from .openai_adapter import OpenAIConnector
from .anthropic_adapter import AnthropicConnector
from .gemini_adapter import GeminiConnector
from .perplexity_adapter import PerplexityConnector
from .base import LLMConnector


def load_connectors() -> Dict[str, LLMConnector]:
    return {
        "openai": OpenAIConnector(),
        "anthropic": AnthropicConnector(),
        "gemini": GeminiConnector(),
        "perplexity": PerplexityConnector(),
    }