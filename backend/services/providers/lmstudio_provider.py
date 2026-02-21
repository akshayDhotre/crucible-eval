from __future__ import annotations

import os

import httpx

from .base import BaseLLMProvider


class LMStudioProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self.base_url = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234").rstrip("/")
        self.model = self.resolve_model("local-model")
        self.timeout = float(os.getenv("LOCAL_LLM_TIMEOUT_SECONDS", "20"))

    async def generate(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/v1/chat/completions", json=payload)
                response.raise_for_status()
                body = response.json()
            choices = body.get("choices", [])
            if not choices:
                return "{}"
            content = choices[0].get("message", {}).get("content", "{}")
            return content if isinstance(content, str) else "{}"
        except Exception as exc:
            raise RuntimeError(f"LM Studio provider request failed: {exc}") from exc
