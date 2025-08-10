from typing import Any, Dict, Optional
import time
from app.connectors.base import BaseLLMConnector, LLMConfig, LLMResponse

class GoogleConnector(BaseLLMConnector):
    async def authenticate(self) -> bool:
        return bool(self.config.headers.get("Authorization"))

    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse:
        start = time.perf_counter()
        content = f"[Gemini:{self.config.model_name}] Response to: {prompt[:100]}"
        return LLMResponse(content=content, model_used=self.config.model_name or "gemini-1.5-pro", response_time=time.perf_counter()-start)

    async def test_connection(self) -> Dict[str, Any]:
        ok = await self.authenticate()
        return {"ok": ok, "model": self.config.model_name}