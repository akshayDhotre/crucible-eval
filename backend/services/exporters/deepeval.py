from __future__ import annotations

import json
from typing import Any


def build_deepeval_config(suite: dict[str, Any]) -> str:
    lines = [
        "from deepeval.test_case import LLMTestCase",
        "from deepeval.dataset import EvaluationDataset",
        "",
        "# TODO: Populate actual_output by running your LLM on each input",
        "# TODO: Populate retrieval_context by running your RAG retriever on each input",
        "",
        "test_cases = [",
    ]

    for case in suite.get("testCases", []):
        lines.extend(
            [
                "    LLMTestCase(",
                f"        input={json.dumps(case.get('input', ''))},",
                "        actual_output='',  # fill at runtime",
                f"        expected_output={json.dumps(case.get('expectedOutput') or '')},",
                "        retrieval_context=[]  # fill at runtime",
                "    ),",
            ]
        )

    lines.extend(
        [
            "]",
            "",
            "dataset = EvaluationDataset(test_cases=test_cases)",
            "",
        ]
    )
    return "\n".join(lines)
