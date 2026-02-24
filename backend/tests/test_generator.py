from __future__ import annotations

import unittest
from unittest.mock import patch

from backend.models.schemas import AppDetails, TestSuite
from backend.services.generator import generate_test_suite


class GeneratorTest(unittest.IsolatedAsyncioTestCase):
    async def test_missing_provider_key_falls_back_to_demo(self) -> None:
        details = AppDetails(
            appType="chatbot",
            systemPrompt="You are a safe assistant.",
            description="General Q&A chatbot.",
            domain="healthcare",
            provider="anthropic",
            testCaseCount=10,
            outputFormat="raw",
        )

        with patch.dict(
            "os.environ",
            {"DEMO_MODE_ENABLED": "true", "ANTHROPIC_API_KEY": "", "OPENAI_API_KEY": "", "GOOGLE_API_KEY": ""},
            clear=False,
        ):
            suite, filename, mime_type, _ = await generate_test_suite(details)

        self.assertEqual(suite.totalCases, 10)
        self.assertIn(suite.frameworkConfig.get("mode"), {"demo-static", "demo-local-ollama", "demo-local-lmstudio"})
        self.assertTrue(filename.startswith("crucible_chatbot_raw_"))
        self.assertTrue(filename.endswith(".json"))
        self.assertEqual(mime_type, "application/json")

    async def test_demo_disabled_without_provider_key_raises(self) -> None:
        details = AppDetails(
            appType="rag",
            systemPrompt="You answer from policy text only.",
            description="Support bot for return policy.",
            domain="e-commerce",
            provider="openai",
            testCaseCount=10,
            outputFormat="promptfoo",
        )

        with patch.dict(
            "os.environ",
            {"DEMO_MODE_ENABLED": "false", "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": "", "GOOGLE_API_KEY": ""},
            clear=False,
        ):
            with self.assertRaises(RuntimeError) as ctx:
                await generate_test_suite(details)

        self.assertIn("demo mode is disabled", str(ctx.exception).lower())

    async def test_local_llm_success_sets_local_mode(self) -> None:
        details = AppDetails(
            appType="rag",
            systemPrompt="You answer from policy text only.",
            description="Support bot for return policy.",
            domain="e-commerce",
            provider="openai",
            testCaseCount=10,
            outputFormat="promptfoo",
        )

        fake_suite = TestSuite(appType="rag", testCases=[])
        with patch.dict(
            "os.environ",
            {
                "DEMO_MODE_ENABLED": "true",
                "DEMO_PROVIDER": "ollama",
                "OPENAI_API_KEY": "",
                "ANTHROPIC_API_KEY": "",
                "GOOGLE_API_KEY": "",
            },
            clear=False,
        ):
            async def fake_generate_with_provider(details_obj: AppDetails) -> TestSuite:
                self.assertEqual(details_obj.provider, "ollama")
                return fake_suite

            with patch("backend.services.generator._generate_with_provider", side_effect=fake_generate_with_provider):
                suite, _, _, _ = await generate_test_suite(details)

        self.assertEqual(suite.frameworkConfig.get("mode"), "demo-local-ollama")

    async def test_deepeval_export_uses_python_file(self) -> None:
        details = AppDetails(
            appType="rag",
            systemPrompt="You answer from policy text only.",
            description="Support bot for return policy.",
            domain="e-commerce",
            provider="openai",
            testCaseCount=10,
            outputFormat="deepeval",
        )

        with patch.dict(
            "os.environ",
            {"DEMO_MODE_ENABLED": "true", "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": "", "GOOGLE_API_KEY": ""},
            clear=False,
        ):
            _, filename, mime_type, export_content = await generate_test_suite(details)

        self.assertTrue(filename.endswith(".py"))
        self.assertEqual(mime_type, "text/x-python")
        self.assertIn("LLMTestCase(", export_content)


if __name__ == "__main__":
    unittest.main()
