from typing import Any, Dict, Optional
import time
from app.connectors.base import BaseLLMConnector, LLMConfig, LLMResponse

class OllamaConnector(BaseLLMConnector):
    async def authenticate(self) -> bool:
        return True

    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse:
        start = time.perf_counter()
        content = f"[Ollama:{self.config.model_name or 'llama3'}] Response to: {prompt[:100]}"
        return LLMResponse(content=content, model_used=self.config.model_name or "llama3", response_time=time.perf_counter()-start)

    async def test_connection(self) -> Dict[str, Any]:
        return {"ok": True, "model": self.config.model_name or "llama3"}