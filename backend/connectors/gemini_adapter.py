import os
from tenacity import retry, wait_exponential, stop_after_attempt
import google.generativeai as genai

from .base import LLMConnector, ConnectorUnavailable


class GeminiConnector(LLMConnector):
    def __init__(self, id: str, label: str, capabilities):
        super().__init__(id=id, label=label, provider="gemini", capabilities=capabilities)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ConnectorUnavailable("gemini", "Missing GEMINI_API_KEY")
        genai.configure(api_key=api_key)

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def generate(self, prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
        try:
            model = genai.GenerativeModel(model_id)
            resp = await model.generate_content_async(prompt, generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            })
            return (resp.text or "").strip()
        except Exception as e:
            raise ConnectorUnavailable("gemini", str(e))