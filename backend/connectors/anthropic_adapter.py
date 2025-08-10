import os
from tenacity import retry, wait_exponential, stop_after_attempt
import anthropic

from .base import LLMConnector, ConnectorUnavailable


class AnthropicConnector(LLMConnector):
    def __init__(self, id: str, label: str, capabilities):
        super().__init__(id=id, label=label, provider="anthropic", capabilities=capabilities)
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ConnectorUnavailable("anthropic", "Missing ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic()

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def generate(self, prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
        try:
            resp = self.client.messages.create(
                model=model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            # anthropic returns content list
            return "".join([blk.text for blk in resp.content if getattr(blk, "text", None)]).strip()
        except Exception as e:
            raise ConnectorUnavailable("anthropic", str(e))