from typing import Any, Dict, Optional
import time
import httpx
from app.connectors.base import BaseLLMConnector, LLMConfig, LLMResponse

class CustomConnector(BaseLLMConnector):
    async def authenticate(self) -> bool:
        return bool(self.config.api_url)

    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse:
        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"prompt": prompt, "context": context, "model": self.config.model_name, "max_tokens": self.config.max_tokens, "temperature": self.config.temperature}
            headers = self.config.headers or {}
            try:
                resp = await client.post(self.config.api_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                content = data.get("content") or data.get("text") or str(data)
            except Exception as exc:
                content = f"Error: {exc}"
        return LLMResponse(content=content, model_used=self.config.model_name or "custom", response_time=time.perf_counter()-start)

    async def test_connection(self) -> Dict[str, Any]:
        return {"ok": await self.authenticate(), "url": self.config.api_url}