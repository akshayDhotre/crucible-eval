from __future__ import annotations

import os


class BaseLLMProvider:
    async def generate(self, system: str, user: str) -> str:
        raise NotImplementedError

    @staticmethod
    def resolve_model(default_model: str, provider_env_var: str = "") -> str:
        if provider_env_var:
            specific = os.getenv(provider_env_var, "").strip()
            if specific:
                return specific
        return os.getenv("DEFAULT_MODEL_NAME", "").strip() or default_model
