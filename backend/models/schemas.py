from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

AppType = Literal["rag", "chatbot", "agent", "codegen", "custom"]
Provider = Literal["openai", "anthropic", "google", "ollama", "lmstudio"]
OutputFormat = Literal["promptfoo", "deepeval", "ragas", "raw"]
Severity = Literal["critical", "high", "medium", "low"]

TestCategory = Literal[
    "happy_path",
    "adversarial",
    "edge_case",
    "refusal",
    "hallucination_probe",
    "context_relevance",
    "jailbreak",
    "prompt_injection",
    "off_topic",
]


class ExampleInteraction(BaseModel):
    input: str = Field(min_length=1)
    output: str = Field(min_length=1)


def _default_provider() -> Provider:
    value = os.getenv("DEFAULT_PROVIDER", "openai").strip().lower()
    allowed = {"openai", "anthropic", "google", "ollama", "lmstudio"}
    return value if value in allowed else "openai"


class AppDetails(BaseModel):
    appType: AppType
    systemPrompt: str = Field(min_length=20)
    description: str = Field(min_length=10)
    domain: str = Field(min_length=2)
    exampleInteractions: list[ExampleInteraction] = Field(default_factory=list)
    provider: Provider = Field(default_factory=_default_provider)
    testCaseCount: Literal[10, 25, 50] = 25
    outputFormat: OutputFormat = "raw"


class TestCase(BaseModel):
    id: str
    category: TestCategory
    input: str
    expectedOutput: str | None = None
    evalCriteria: list[str] = Field(default_factory=list)
    severity: Severity = "medium"
    notes: str | None = None


class BenchmarkRef(BaseModel):
    name: str
    reason: str
    link: str | None = None


class TestSuite(BaseModel):
    appType: AppType
    generatedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    totalCases: int = 0
    testCases: list[TestCase] = Field(default_factory=list)
    benchmarks: list[BenchmarkRef] = Field(default_factory=list)
    frameworkConfig: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def sync_total_cases(self) -> "TestSuite":
        self.totalCases = len(self.testCases)
        return self


class GenerateResponse(BaseModel):
    suite: TestSuite
    exportFilename: str
    exportMimeType: str
    exportContent: str
