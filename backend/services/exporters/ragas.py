from __future__ import annotations

from typing import Any


def build_ragas_dataset(suite: dict[str, Any]) -> dict[str, Any]:
    """Build a RAGAS-compatible dataset from a Crucible test suite.

    Output format is compatible with RAGAS evaluation and includes:
    - Standard RAGAS fields: question, answer, contexts, ground_truth
    - Extended Crucible metadata: _categories, _eval_criteria, _severity

    The extended fields enable richer analysis in evaluation notebooks,
    allowing breakdown of metrics by test category (happy_path, adversarial, etc.)
    """
    questions: list[str] = []
    answers: list[str] = []
    contexts: list[list[str]] = []
    ground_truth: list[str] = []

    # Extended metadata for richer evaluation analysis
    categories: list[str] = []
    eval_criteria: list[list[str]] = []
    severity: list[str] = []
    notes: list[str] = []

    for case in suite.get("testCases", []):
        questions.append(case.get("input", ""))
        answers.append("")  # To be filled by RAG pipeline
        contexts.append([])  # To be filled by RAG pipeline
        ground_truth.append(case.get("expectedOutput") or "")

        # Capture test case metadata
        categories.append(case.get("category", "unknown"))
        eval_criteria.append(case.get("evalCriteria", []))
        severity.append(case.get("severity", "medium"))
        notes.append(case.get("notes") or "")

    return {
        # Instructions for users
        "_instructions": (
            "Fill 'answer' with your LLM's actual response and 'contexts' with "
            "retrieved chunks from your RAG pipeline before running RAGAS metrics. "
            "The '_categories' and '_eval_criteria' fields enable breakdown by test type."
        ),
        # Standard RAGAS fields
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truth,
        # Extended Crucible metadata (prefixed with _ to indicate non-RAGAS fields)
        "_categories": categories,
        "_eval_criteria": eval_criteria,
        "_severity": severity,
        "_notes": notes,
        # Metadata about the export
        "_app_type": suite.get("appType", "unknown"),
        "_total_cases": len(questions),
        "_generated_at": suite.get("generatedAt", ""),
    }
