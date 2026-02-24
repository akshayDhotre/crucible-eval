# Crucible Eval

Crucible Eval is an evaluation-suite factory for LLM applications.

It turns app context (system prompt, domain, app type, provider preferences) into runnable artifacts for standard evaluation frameworks:
- Promptfoo
- DeepEval
- Ragas

The goal is to reduce the gap between "we should evaluate" and "we are running repeatable evals in CI/QA".

## Why This Exists

Teams building LLM applications often hit the same problems:
1. Evaluation strategy is unclear or inconsistent across teams.
2. Test cases are mostly happy-path and miss adversarial/edge behavior.
3. Framework setup is manual and slows adoption.
4. Output schemas drift, making results hard to compare over time.

Crucible Eval addresses this by generating structured, framework-ready suites while enforcing important eval constraints (category coverage, schema validation, and provider-aware output handling).

## What It Does

Given app details, Crucible Eval generates:
1. A categorized test suite (happy path, adversarial, edge-case, safety probes, etc.).
2. Exported configs for Promptfoo, DeepEval, and Ragas.
3. Benchmark recommendations mapped by app type and domain.
4. Downloadable artifacts with deterministic naming for traceability.

## Exporter Runtime Fields

### Ragas Export (`.json`)

Ragas export is a dataset scaffold. Before running metrics, you must populate:
1. `answer`: the actual response produced by your LLM for each `question`.
2. `contexts`: retrieved document chunks from your RAG retriever for each `question`.

Notes:
1. Crucible intentionally exports `contexts` as empty lists (`[]`) because retrieval data is runtime-specific.
2. The file includes a top-level `_instructions` key as a reminder of what to fill.

### DeepEval Export (`.py`)

DeepEval export is a runnable Python dataset script using `LLMTestCase` and `EvaluationDataset`.

Before evaluating, you must populate:
1. `actual_output`: the actual model output for each test input.
2. `retrieval_context`: retrieved RAG chunks for each test input (if applicable).

Notes:
1. Crucible does not emit a DeepEval JSON format because DeepEval is a Python-native library.
2. The generated script is intentionally minimal and directly executable after those runtime fields are filled.

## Why Multiple LLM Providers

Different teams have different platform constraints (cost, latency, legal/privacy, model capability, regional availability).

Crucible Eval supports:
- OpenAI
- Anthropic
- Google
- Ollama
- LM Studio

Provider abstraction enables:
1. Switching vendors without rewriting core test-generation logic.
2. Local/offline experimentation via Ollama/LM Studio.
3. Unified downstream exports regardless of upstream generation provider.

## Core Nuances Considered

This project intentionally handles concerns beyond "send prompt, return template":
1. Strict JSON schema validation for generated outputs.
2. Retry path when model responses are malformed.
3. Provider-specific generation behavior and failure modes.
4. Mode fallback logic:
   - Live provider when configured.
   - Local provider fallback (Ollama/LM Studio) when cloud keys are absent.
   - Static deterministic demo fallback when local provider is unavailable.
5. App-type-aware prompting strategy (RAG/agent/chatbot/codegen/custom).
6. Benchmark enrichment by app type and domain.
7. Framework-specific exporter shaping (not one generic dump).
8. UX guidance to improve generation quality (system prompt quality, domain specificity, examples).

## Architecture

High-level flow:
1. User submits app details from `frontend/`.
2. `backend/` selects a prompt template by app type.
3. Provider layer generates structured test JSON.
4. Backend validates and enriches suite.
5. Exporter layer emits framework-specific output.
6. UI renders preview/table and download actions.

### Project Structure

- `frontend/`: Next.js app (App Router), form + result UX.
- `backend/`: FastAPI service, providers, generator orchestration, exporters.
- `notebooks/`: usage demos for Ragas and DeepEval.

## Tech Stack and Tradeoffs

### Frontend
- Next.js 14 + TypeScript + Tailwind + Zustand

Why:
- Fast iteration on form/results UX.
- Strong typing and predictable state.

Tradeoffs:
- Lightweight local state is simpler now, but multi-user collaboration features would eventually need persistent storage/auth.

### Backend
- FastAPI + Pydantic + provider adapters

Why:
- Strong schema validation and easy async orchestration.
- Python ecosystem alignment with eval tooling and experimentation workflows.

Tradeoffs:
- Polyglot stack (TS + Python) adds operational overhead versus a single-language stack.

### Local/Cloud Provider Strategy

Why:
- Improves reliability and dev productivity when cloud keys are unavailable.

Tradeoffs:
- Local provider output quality can vary by model/runtime setup.
- Requires clear mode signaling (`live`, `demo-local-*`, `demo-static`) to avoid confusion.

## Run Locally

1. Copy env vars
```bash
cp .env.example .env
```

2. Backend
```bash
uv python install 3.12
uv venv --python 3.12 backend/.venv
uv sync --project backend
uv run --project backend uvicorn backend.main:app --reload --port 8000
```

3. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Configuration

Key `.env` variables:
- `DEFAULT_PROVIDER=openai|anthropic|google|ollama|lmstudio`
- `DEFAULT_MODEL_NAME=<model_name>`
- `OPENAI_API_KEY=`
- `ANTHROPIC_API_KEY=`
- `GOOGLE_API_KEY=`
- `OLLAMA_BASE_URL=http://127.0.0.1:11434`
- `LMSTUDIO_BASE_URL=http://127.0.0.1:1234`
- `DEMO_MODE_ENABLED=true|false`
- `DEMO_PROVIDER=ollama|lmstudio`
- `LOCAL_LLM_TIMEOUT_SECONDS=20`

## API

`POST /generate`

Schema references:
- `backend/models/schemas.py`
- `frontend/lib/types.ts`

Response includes:
- `suite`
- `exportFilename`
- `exportMimeType`
- `exportContent`

## Notebooks (End-to-End Demos)

- `notebooks/ragas_usage_demo.ipynb`
- `notebooks/deepeval_usage_demo.ipynb`

These notebooks are path-agnostic and resolve from repo root. They auto-pick latest exports in `downloads/`.

## Future Improvements

1. Add CI pipelines for regression checks across exporters and provider adapters.
2. Add richer eval metric presets by app type (e.g., RAG faithfulness bundles, agent tool-use bundles).
3. Add multi-suite versioning and historical comparison UI.
4. Add endpoint-targeted "execution-ready" exports with minimal manual wiring.
5. Add stronger benchmark metadata (links, constraints, expected task fit).
6. Add auth + shared workspaces for team usage.
7. Add plugin interface for custom exporters and custom provider adapters.
8. Add optional DB for run history, lineage, and reproducibility metadata.

## Contributing

Contributions are encouraged, especially ideas that improve evaluation quality, reliability, and interoperability.

Please read `CONTRIBUTING.md` before opening a PR.

Good contribution areas:
1. New provider adapters or provider-specific robustness improvements.
2. Better exporter fidelity for Promptfoo/DeepEval/Ragas versions.
3. Additional eval categories and domain-aware heuristics.
4. Better UX for reviewing, filtering, and comparing test suites.
5. CI tooling, quality gates, and reproducibility tooling.
6. Documentation, guides, and realistic sample scenarios.

Please open an issue/PR with:
- problem statement,
- proposed approach,
- expected impact,
- validation plan.

## Security Notes For Public Repos

Before publishing publicly:
1. Never commit `.env` or real secrets.
2. Rotate any key that may have been exposed historically.
3. Keep provider credentials in local env or secret managers.
4. If deploying publicly, add auth, rate limits, and strict CORS.

Quick check before pushing:
```bash
rg -n "(OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_API_KEY|sk-[A-Za-z0-9]|BEGIN (RSA|OPENSSH) PRIVATE KEY)" .
git status
```

## Governance Files

- `LICENSE` (MIT)
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
