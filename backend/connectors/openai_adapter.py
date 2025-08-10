import os
from tenacity import retry, wait_exponential, stop_after_attempt
from openai import AsyncOpenAI

from .base import LLMConnector, ConnectorUnavailable


class OpenAIConnector(LLMConnector):
    def __init__(self, id: str, label: str, capabilities):
        super().__init__(id=id, label=label, provider="openai", capabilities=capabilities)
        if not os.getenv("OPENAI_API_KEY"):
            raise ConnectorUnavailable("openai", "Missing OPENAI_API_KEY")
        self.client = AsyncOpenAI()

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def generate(self, prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
        try:
            resp = await self.client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            raise ConnectorUnavailable("openai", str(e))