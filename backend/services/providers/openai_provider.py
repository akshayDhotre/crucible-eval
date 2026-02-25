from __future__ import annotations

import os

from openai import AsyncOpenAI

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = self.resolve_model("gpt-4o", "OPENAI_MODEL_NAME")

    async def generate(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.7,
        }

        try:
            response = await self.client.chat.completions.create(**payload)
            return response.choices[0].message.content or "{}"
        except Exception as exc:
            message = str(exc)
            if "temperature" in message and "Only the default (1) value is supported" in message:
                try:
                    payload.pop("temperature", None)
                    response = await self.client.chat.completions.create(**payload)
                    return response.choices[0].message.content or "{}"
                except Exception as retry_exc:
                    raise RuntimeError(f"OpenAI provider request failed: {retry_exc}") from retry_exc

            raise RuntimeError(f"OpenAI provider request failed: {exc}") from exc
