from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, cast
from uuid import uuid4

from backend.models.schemas import AppDetails, BenchmarkRef, TestCase, TestSuite
from backend.services.exporters.deepeval import build_deepeval_config
from backend.services.exporters.promptfoo import build_promptfoo_config
from backend.services.exporters.ragas import build_ragas_dataset
from backend.services.providers.anthropic_provider import AnthropicProvider
from backend.services.providers.base import BaseLLMProvider
from backend.services.providers.google_provider import GoogleProvider
from backend.services.providers.lmstudio_provider import LMStudioProvider
from backend.services.providers.ollama_provider import OllamaProvider
from backend.services.providers.openai_provider import OpenAIProvider

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"
PROVIDER_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
}

TEMPLATE_MAP = {
    "rag": "rag_template.txt",
    "agent": "agent_template.txt",
    "chatbot": "chatbot_template.txt",
    "codegen": "codegen_template.txt",
    "custom": "system_prompt.txt",
}

BENCHMARK_MAP = {
    "rag": ["RAGAS metrics", "BEIR", "MS MARCO", "HotpotQA"],
    "chatbot": ["MT-Bench", "Chatbot Arena", "HELM", "BIG-Bench"],
    "agent": ["AgentBench", "ToolBench", "GAIA", "WebArena"],
    "codegen": ["HumanEval", "MBPP", "SWE-bench", "LiveCodeBench"],
    "custom": ["HELM", "BIG-Bench"],
}

DOMAIN_ADDITIONS = {
    "healthcare": ["MedQA", "PubMedQA", "MedMCQA"],
    "legal": ["LegalBench", "CaseHOLD"],
    "finance": ["FinanceBench", "ConvFinQA"],
}

DEMO_CATEGORIES = [
    "happy_path",
    "adversarial",
    "edge_case",
    "hallucination_probe",
    "prompt_injection",
    "context_relevance",
    "off_topic",
    "refusal",
    "jailbreak",
]

Mode = Literal["live", "demo-local-ollama", "demo-local-lmstudio", "demo-static"]


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _build_provider(name: str) -> BaseLLMProvider:
    if name == "openai":
        return OpenAIProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "google":
        return GoogleProvider()
    if name == "ollama":
        return OllamaProvider()
    if name == "lmstudio":
        return LMStudioProvider()
    raise ValueError(f"Unsupported provider: {name}")


def _provider_is_configured(name: str) -> bool:
    if name in {"ollama", "lmstudio"}:
        return True
    key_name = PROVIDER_KEY_MAP[name]
    return bool(os.getenv(key_name, "").strip())


def _demo_mode_enabled() -> bool:
    return os.getenv("DEMO_MODE_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}


def _demo_provider() -> str:
    raw = os.getenv("DEMO_PROVIDER", os.getenv("DEMO_LOCAL_PROVIDER", "ollama")).strip().lower()
    return raw if raw in {"ollama", "lmstudio"} else "ollama"


def _benchmarks(app_type: str, domain: str) -> list[BenchmarkRef]:
    base = BENCHMARK_MAP.get(app_type, [])
    additions = DOMAIN_ADDITIONS.get(domain.lower(), [])
    merged = list(dict.fromkeys([*base, *additions]))
    return [BenchmarkRef(name=item, reason=f"Relevant for {app_type} apps in {domain}") for item in merged]


def _build_user_prompt(details: AppDetails) -> str:
    examples = [{"input": i.input, "output": i.output} for i in details.exampleInteractions
    ]
    payload = {
        "appType": details.appType,
        "systemPrompt": details.systemPrompt,
        "description": details.description,
        "domain": details.domain,
        "exampleInteractions": examples,
        "requiredCount": details.testCaseCount,
        "requirements": {
            "adversarialMinimumPercent": 30,
            "strictJson": True,
            "categoriesRequired": [
                "happy_path",
                "adversarial",
                "edge_case",
                "hallucination_probe",
                "prompt_injection",
            ],
        },
    }
    return json.dumps(payload, indent=2)


def _build_demo_suite(details: AppDetails) -> TestSuite:
    cases: list[TestCase] = []
    domain_prefix = f"{details.domain.title()} app"

    for idx in range(details.testCaseCount):
        category = cast(Any, DEMO_CATEGORIES[idx % len(DEMO_CATEGORIES)])
        case_id = f"demo-{idx + 1:03d}-{uuid4().hex[:8]}"
        prompt = f"[{domain_prefix}] Scenario {idx + 1}: validate {category} behavior for the current system prompt."
        expected = f"Response should follow policy constraints and remain aligned with {details.appType} intent."
        criteria = ["task_success", "no_hallucination", "instruction_following"]
        severity = cast(Any, "high" if category in {"adversarial", "prompt_injection", "jailbreak"} else "medium")

        cases.append(
            TestCase(
                id=case_id,
                category=category,
                input=prompt,
                expectedOutput=expected,
                evalCriteria=criteria,
                severity=severity,
                notes="demo_mode_generated",
            )
        )

    return TestSuite(
        appType=details.appType,
        generatedAt=datetime.now(timezone.utc).isoformat(),
        testCases=cases,
        benchmarks=_benchmarks(details.appType, details.domain),
        frameworkConfig={"format": details.outputFormat},
    )


def _export_content(suite: TestSuite, output_format: str, provider: str) -> tuple[str, str, str, dict[str, Any]]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base = f"crucible_{suite.appType}_{output_format}_{timestamp}"
    as_dict = suite.model_dump()
    if output_format == "promptfoo":
        content = build_promptfoo_config(as_dict, provider)
        return f"{base}.yaml", "application/x-yaml", content, {"format": "promptfoo"}
    if output_format == "deepeval":
        data = build_deepeval_config(as_dict)
        content = json.dumps(data, indent=2)
        return f"{base}.json", "application/json", content, {"format": "deepeval"}
    if output_format == "ragas":
        data = build_ragas_dataset(as_dict)
        content = json.dumps(data, indent=2)
        return f"{base}.json", "application/json", content, {"format": "ragas"}
    content = json.dumps(as_dict, indent=2)
    return f"{base}.json", "application/json", content, {"format": "raw"}


async def _generate_with_provider(details: AppDetails) -> TestSuite:
    system = _load_prompt("system_prompt.txt")
    template = _load_prompt(TEMPLATE_MAP[details.appType])
    user = _build_user_prompt(details)

    provider = _build_provider(details.provider)
    parse_error: Exception | None = None

    for attempt in range(2):
        try:
            raw = await asyncio.wait_for(provider.generate(f"{system}\n\n{template}", user), timeout=60)
            suite = TestSuite.model_validate_json(raw)
            suite.appType = details.appType
            suite.benchmarks = _benchmarks(details.appType, details.domain)
            return suite
        except asyncio.TimeoutError as exc:
            raise RuntimeError("Provider timed out while generating test cases") from exc
        except Exception as exc:
            parse_error = exc
            if attempt == 0:
                user = user + "\n\nIMPORTANT: previous output was invalid. Return valid JSON only."
                continue

    raise RuntimeError(f"LLM output validation failed after retry: {parse_error}")


async def generate_test_suite(details: AppDetails) -> tuple[TestSuite, str, str, str]:
    mode: Mode = "live"
    requested_provider = details.provider

    if _provider_is_configured(requested_provider):
        try:
            suite = await _generate_with_provider(details)
        except Exception as exc:
            if not _demo_mode_enabled():
                raise
            if requested_provider in {"ollama", "lmstudio"}:
                suite = _build_demo_suite(details)
                mode = "demo-static"
            else:
                raise exc
    else:
        if not _demo_mode_enabled():
            raise RuntimeError(f"{PROVIDER_KEY_MAP[requested_provider]} is not configured and demo mode is disabled")

        demo_provider = _demo_provider()
        demo_details = details.model_copy(update={"provider": demo_provider})
        try:
            suite = await _generate_with_provider(demo_details)
            mode = cast(Mode, f"demo-local-{demo_provider}")
        except Exception:
            suite = _build_demo_suite(details)
            mode = "demo-static"

    filename, mime_type, export_content, framework = _export_content(suite, details.outputFormat, details.provider)
    suite.frameworkConfig = framework | {"mode": mode}
    return suite, filename, mime_type, export_content
