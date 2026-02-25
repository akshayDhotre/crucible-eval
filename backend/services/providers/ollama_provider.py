from __future__ import annotations

import os

import httpx

from .base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        self.model = self.resolve_model("deepseek-r1", "OLLAMA_MODEL_NAME")
        self.timeout = float(os.getenv("LOCAL_LLM_TIMEOUT_SECONDS", "120"))

    async def generate(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                body = response.json()
            message = body.get("message", {})
            content = message.get("content", "{}") if isinstance(message, dict) else "{}"
            return content if isinstance(content, str) else "{}"
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise RuntimeError(
                    f"Ollama model '{self.model}' not found. "
                    f"Run: ollama pull {self.model}  "
                    f"Or set DEFAULT_MODEL_NAME in .env to a model you have installed."
                ) from exc
            raise RuntimeError(f"Ollama provider request failed: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Ollama provider request failed: {exc}") from exc
