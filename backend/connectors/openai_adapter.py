import os
import asyncio
import httpx
from .base import LLMConnector, ConnectorUnavailable

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class OpenAIConnector(LLMConnector):
    def __init__(self):
        super().__init__(
            id="openai",
            label="OpenAI",
            provider="openai",
            capabilities={"expand": True, "critique": True, "synth": True},
        )

    async def generate(self, prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
        if not OPENAI_API_KEY:
            raise ConnectorUnavailable("openai", "Missing OPENAI_API_KEY")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
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
        raise ConnectorUnavailable("openai", "Failed after retries")