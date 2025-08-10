import os
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt

from .base import LLMConnector, ConnectorUnavailable


class PerplexityConnector(LLMConnector):
    def __init__(self, id: str, label: str, capabilities):
        super().__init__(id=id, label=label, provider="perplexity", capabilities=capabilities)
        if not os.getenv("PERPLEXITY_API_KEY"):
            raise ConnectorUnavailable("perplexity", "Missing PERPLEXITY_API_KEY")
        self.api_key = os.getenv("PERPLEXITY_API_KEY")

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def generate(self, prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": model_id,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post("https://api.perplexity.ai/chat/completions", headers=headers, json=data)
                resp.raise_for_status()
                js = resp.json()
                return js["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise ConnectorUnavailable("perplexity", str(e))