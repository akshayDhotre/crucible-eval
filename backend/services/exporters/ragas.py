from __future__ import annotations

from typing import Any


def build_ragas_dataset(suite: dict[str, Any]) -> dict[str, Any]:
    questions: list[str] = []
    answers: list[str] = []
    contexts: list[list[str]] = []
    ground_truth: list[str] = []

    for case in suite.get("testCases", []):
        questions.append(case.get("input", ""))
        answers.append("")
        contexts.append([])
        ground_truth.append(case.get("expectedOutput") or "")

    return {
        "_instructions": (
            "Fill 'answer' with your LLM's actual response and 'contexts' with "
            "retrieved chunks from your RAG pipeline before running Ragas metrics."
        ),
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truth,
    }
