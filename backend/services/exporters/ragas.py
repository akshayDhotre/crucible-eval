from __future__ import annotations

from typing import Any


def build_ragas_dataset(suite: dict[str, Any]) -> dict[str, list[Any]]:
    questions: list[str] = []
    answers: list[str] = []
    contexts: list[list[str]] = []
    ground_truth: list[str] = []

    for case in suite.get("testCases", []):
        questions.append(case.get("input", ""))
        answers.append("")

        context_chunks: list[str] = []
        if case.get("notes"):
            context_chunks.append(str(case["notes"]))
        if case.get("category"):
            context_chunks.append(f"category:{case['category']}")
        contexts.append(context_chunks)

        ground_truth.append(case.get("expectedOutput") or "")

    return {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truth,
    }
