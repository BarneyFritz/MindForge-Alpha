from __future__ import annotations
import os
from typing import Dict
import google.generativeai as genai
from .base import BaseLLMConnector, ConnectorRegistry

@ConnectorRegistry.register
class GeminiConnector(BaseLLMConnector):
    name = "gemini"
    default_model = "gemini-1.5-flash"

    def __init__(self):
        super().__init__(api_key_env="GOOGLE_API_KEY")
        self.model = None
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.default_model)

    async def generate(self, prompt: str) -> dict:
        if not self.model:
            return {"text": f"[stub-gemini] Ideas for: {prompt[:80]}...", "model": self.default_model, "confidence": 0.5}
        resp = self.model.generate_content(prompt)
        text = resp.text if hasattr(resp, "text") else str(resp)
        return {"text": text, "model": self.default_model, "confidence": 0.7}

    async def critique(self, prompt: str, peers: Dict[str, str]) -> dict:
        if not self.model:
            return {"text": f"[stub-gemini] Focused critique for: {prompt[:60]}...", "model": self.default_model, "confidence": 0.5}
        peer_text = "\n".join([f"[{k}] {v}" for k, v in peers.items()])
        resp = self.model.generate_content(
            f"Provide brief, pointed critique of peers' ideas. No fluff.\nPrompt: {prompt}\nPeers:\n{peer_text}"
        )
        text = resp.text if hasattr(resp, "text") else str(resp)
        return {"text": text, "model": self.default_model, "confidence": 0.7}