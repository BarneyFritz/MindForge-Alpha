import os
import asyncio
import httpx
from .base import LLMConnector, ConnectorUnavailable

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class GeminiConnector(LLMConnector):
    def __init__(self):
        super().__init__(
            id="gemini",
            label="Gemini",
            provider="gemini",
            capabilities={"expand": True, "critique": True, "synth": True},
        )

    async def generate(self, prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
        if not GEMINI_API_KEY:
            raise ConnectorUnavailable("gemini", "Missing GEMINI_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    r = await client.post(url, json=payload)
                if r.status_code == 200:
                    data = r.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text = "".join([p.get("text", "") for p in parts])
                        return text.strip()
                await asyncio.sleep(1.5 * (attempt + 1))
            except Exception:
                await asyncio.sleep(1.5 * (attempt + 1))
        raise ConnectorUnavailable("gemini", "Failed after retries")