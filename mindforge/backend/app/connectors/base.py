from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
import time

class LLMConfig(BaseModel):
    name: str
    api_url: str
    headers: Dict[str, str] = {}
    model_name: Optional[str] = None
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.7

class LLMResponse(BaseModel):
    content: str
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    model_used: str
    response_time: float

class BaseLLMConnector(ABC):
    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    async def authenticate(self) -> bool: ...

    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse: ...

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]: ...

    def get_model_info(self) -> Dict[str, Any]:
        return {"name": self.config.name, "model": self.config.model_name, "api_url": self.config.api_url}