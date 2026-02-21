from __future__ import annotations

from typing import Any


def build_deepeval_config(suite: dict[str, Any]) -> dict[str, Any]:
    cases = []
    for case in suite.get("testCases", []):
        cases.append(
            {
                "id": case.get("id"),
                "input": case.get("input", ""),
                "expected_output": case.get("expectedOutput") or "",
                "context": [case.get("notes")] if case.get("notes") else [],
                "metadata": {
                    "category": case.get("category"),
                    "severity": case.get("severity"),
                    "eval_criteria": case.get("evalCriteria", []),
                },
            }
        )

    return {
        "app_type": suite.get("appType", "custom"),
        "dataset": {
            "type": "EvaluationDataset",
            "test_cases": cases,
        },
    }
