from __future__ import annotations

import os

from google import genai
from google.genai import types

from .base import BaseLLMProvider


class GoogleProvider(BaseLLMProvider):
    def __init__(self) -> None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not configured")
        self.client = genai.Client(api_key=api_key)
        self.model = self.resolve_model("gemini-2.0-flash", "GOOGLE_MODEL_NAME")

    async def generate(self, system: str, user: str) -> str:
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=[f"SYSTEM:\n{system}\n\nUSER:\n{user}"],
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.7),
            )
            return response.text or "{}"
        except Exception as exc:
            raise RuntimeError(f"Google provider request failed: {exc}") from exc
