from __future__ import annotations
import os
from typing import Dict
from openai import OpenAI
from .base import BaseLLMConnector, ConnectorRegistry

@ConnectorRegistry.register
class OpenAIConnector(BaseLLMConnector):
    name = "openai"
    default_model = "gpt-4o-mini"

    def __init__(self):
        super().__init__(api_key_env="OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    async def generate(self, prompt: str) -> dict:
        if not self.client:
            return {"text": f"[stub-openai] Ideas for: {prompt[:80]}...", "model": self.default_model, "confidence": 0.5}
        resp = self.client.chat.completions.create(
            model=self.default_model,
            messages=[
                {"role": "system", "content": "You are a concise legal brainstorming assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        text = resp.choices[0].message.content.strip()
        return {"text": text, "model": self.default_model, "confidence": 0.7}

    async def critique(self, prompt: str, peers: Dict[str, str]) -> dict:
        if not self.client:
            return {"text": f"[stub-openai] Focused critique of peers for: {prompt[:60]}...", "model": self.default_model, "confidence": 0.5}
        peer_text = "\n".join([f"[{k}] {v}" for k, v in peers.items()])
        resp = self.client.chat.completions.create(
            model=self.default_model,
            messages=[
                {"role": "system", "content": "Provide brief, pointed critique. No fluff."},
                {"role": "user", "content": f"Prompt: {prompt}\nPeers:\n{peer_text}"},
            ],
            temperature=0.2,
        )
        text = resp.choices[0].message.content.strip()
        return {"text": text, "model": self.default_model, "confidence": 0.7}