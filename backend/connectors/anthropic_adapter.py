import os
import asyncio
import httpx
from .base import LLMConnector, ConnectorUnavailable

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class AnthropicConnector(LLMConnector):
    def __init__(self):
        super().__init__(
            id="anthropic",
            label="Anthropic",
            provider="anthropic",
            capabilities={"expand": True, "critique": True, "synth": True},
        )

    async def generate(self, prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
        if not ANTHROPIC_API_KEY:
            raise ConnectorUnavailable("anthropic", "Missing ANTHROPIC_API_KEY")
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    r = await client.post(url, headers=headers, json=payload)
                if r.status_code == 200:
                    data = r.json()
                    content = "".join([p.get("text", "") for p in data.get("content", [])])
                    return content.strip()
                await asyncio.sleep(1.5 * (attempt + 1))
            except Exception:
                await asyncio.sleep(1.5 * (attempt + 1))
        raise ConnectorUnavailable("anthropic", "Failed after retries")