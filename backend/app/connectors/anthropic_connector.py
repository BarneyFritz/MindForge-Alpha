from __future__ import annotations
import os
from typing import Dict
import anthropic
from .base import BaseLLMConnector, ConnectorRegistry

@ConnectorRegistry.register
class AnthropicConnector(BaseLLMConnector):
    name = "anthropic"
    default_model = "claude-3-haiku-20240307"

    def __init__(self):
        super().__init__(api_key_env="ANTHROPIC_API_KEY")
        self.client = None
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    async def generate(self, prompt: str) -> dict:
        if not self.client:
            return {"text": f"[stub-claude] Ideas for: {prompt[:80]}...", "model": self.default_model, "confidence": 0.5}
        msg = self.client.messages.create(
            model=self.default_model,
            max_tokens=600,
            temperature=0.4,
            system="You are a concise legal brainstorming assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join([b.text for b in msg.content if hasattr(b, "text")])
        return {"text": text, "model": self.default_model, "confidence": 0.7}

    async def critique(self, prompt: str, peers: Dict[str, str]) -> dict:
        if not self.client:
            return {"text": f"[stub-claude] Focused critique for: {prompt[:60]}...", "model": self.default_model, "confidence": 0.5}
        peer_text = "\n".join([f"[{k}] {v}" for k, v in peers.items()])
        msg = self.client.messages.create(
            model=self.default_model,
            max_tokens=500,
            temperature=0.2,
            system="Provide brief, pointed critique. No fluff.",
            messages=[{"role": "user", "content": f"Prompt: {prompt}\nPeers:\n{peer_text}"}],
        )
        text = "".join([b.text for b in msg.content if hasattr(b, "text")])
        return {"text": text, "model": self.default_model, "confidence": 0.7}