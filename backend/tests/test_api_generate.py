from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


class GenerateApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_generate_returns_contract_shape(self) -> None:
        payload = {
            "appType": "rag",
            "systemPrompt": "You answer only from approved docs.",
            "description": "Policy QA assistant",
            "domain": "e-commerce",
            "provider": "openai",
            "testCaseCount": 10,
            "outputFormat": "promptfoo",
            "exampleInteractions": [],
        }

        with patch.dict(
            "os.environ",
            {"DEMO_MODE_ENABLED": "true", "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": "", "GOOGLE_API_KEY": ""},
            clear=False,
        ):
            response = self.client.post("/generate", json=payload)

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertIn("suite", body)
        self.assertIn("exportFilename", body)
        self.assertIn("exportMimeType", body)
        self.assertIn("exportContent", body)

        suite = body["suite"]
        self.assertEqual(suite["totalCases"], 10)
        self.assertIn(suite["frameworkConfig"]["mode"], ["demo-static", "demo-local-ollama", "demo-local-lmstudio"])

    def test_generate_returns_503_when_demo_disabled_and_no_key(self) -> None:
        payload = {
            "appType": "rag",
            "systemPrompt": "You answer only from approved docs.",
            "description": "Policy QA assistant",
            "domain": "e-commerce",
            "provider": "openai",
            "testCaseCount": 10,
            "outputFormat": "promptfoo",
            "exampleInteractions": [],
        }

        with patch.dict(
            "os.environ",
            {"DEMO_MODE_ENABLED": "false", "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": "", "GOOGLE_API_KEY": ""},
            clear=False,
        ):
            response = self.client.post("/generate", json=payload)

        self.assertEqual(response.status_code, 503)
        self.assertIn("demo mode is disabled", response.json().get("detail", "").lower())


if __name__ == "__main__":
    unittest.main()
