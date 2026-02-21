from __future__ import annotations

import os

from anthropic import AsyncAnthropic

from .base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    def __init__(self) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = self.resolve_model("claude-sonnet-4-6")

    async def generate(self, system: str, user: str) -> str:
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.7,
                system=system,
                messages=[
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": "{"},
                ],
            )
            text_chunks = [block.text for block in message.content if getattr(block, "type", "") == "text"]
            joined = "".join(text_chunks)
            return joined if joined.startswith("{") else "{" + joined
        except Exception as exc:
            raise RuntimeError(f"Anthropic provider request failed: {exc}") from exc
