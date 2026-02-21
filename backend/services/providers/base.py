from __future__ import annotations

import os


class BaseLLMProvider:
    async def generate(self, system: str, user: str) -> str:
        raise NotImplementedError

    @staticmethod
    def resolve_model(default_model: str) -> str:
        return os.getenv("DEFAULT_MODEL_NAME", "").strip() or default_model
