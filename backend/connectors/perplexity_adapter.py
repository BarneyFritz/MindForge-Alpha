import os
import asyncio
import httpx
from .base import LLMConnector, ConnectorUnavailable

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


class PerplexityConnector(LLMConnector):
    def __init__(self):
        super().__init__(
            id="perplexity",
            label="Perplexity",
            provider="perplexity",
            capabilities={"expand": True, "critique": True, "synth": True},
        )

    async def generate(self, prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
        if not PERPLEXITY_API_KEY:
            raise ConnectorUnavailable("perplexity", "Missing PERPLEXITY_API_KEY")
        url = "https://api.perplexity.ai/chat/completions"
        headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}"}
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    r = await client.post(url, headers=headers, json=payload)
                if r.status_code == 200:
                    data = r.json()
                    return data["choices"][0]["message"]["content"].strip()
                await asyncio.sleep(1.5 * (attempt + 1))
            except Exception:
                await asyncio.sleep(1.5 * (attempt + 1))
        raise ConnectorUnavailable("perplexity", "Failed after retries")