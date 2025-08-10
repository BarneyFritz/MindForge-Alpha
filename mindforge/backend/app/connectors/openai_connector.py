from typing import Any, Dict, Optional
import httpx
import time
from app.connectors.base import BaseLLMConnector, LLMConfig, LLMResponse

class OpenAIConnector(BaseLLMConnector):
    async def authenticate(self) -> bool:
        return bool(self.config.headers.get("Authorization"))

    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse:
        start = time.perf_counter()
        # Placeholder: In production, call OpenAI API
        content = f"[OpenAI:{self.config.model_name}] Response to: {prompt[:100]}"
        return LLMResponse(content=content, tokens_used=128, cost_estimate=0.01, model_used=self.config.model_name or "gpt-4o", response_time=time.perf_counter()-start)

    async def test_connection(self) -> Dict[str, Any]:
        ok = await self.authenticate()
        return {"ok": ok, "model": self.config.model_name}