# Contributing

Thanks for your interest in improving Crucible Eval.

## Ways to contribute

High-impact areas:
1. Provider adapters and reliability improvements.
2. Export fidelity for Promptfoo, DeepEval, and Ragas.
3. Test-generation quality (coverage, adversarial depth, domain awareness).
4. Frontend UX for review, diffing, and debugging generated suites.
5. Documentation and tutorials for real-world eval workflows.

## Development setup

1. Clone repo and enter project root.
2. Copy env file:
```bash
cp .env.example .env
```
3. Backend setup:
```bash
uv python install 3.12
uv venv --python 3.12 backend/.venv
uv sync --project backend
uv run --project backend uvicorn backend.main:app --reload --port 8000
```
4. Frontend setup (new terminal):
```bash
cd frontend
npm install
npm run dev
```

## Branching and PR flow

1. Create a feature branch.
2. Keep changes focused and atomic.
3. Add/update tests for behavior changes.
4. Update docs when behavior or config changes.
5. Open a PR with:
   - Problem statement
   - Proposed approach
   - Validation evidence (tests/screenshots)
   - Risks and rollback notes

## Quality checks

Run before opening PR:
```bash
UV_CACHE_DIR=/tmp/.uv-cache uv run --project backend python -m unittest discover -s backend/tests -p 'test_*.py' -v
cd frontend && npm run build
```

## Security and secrets

- Never commit `.env` or credentials.
- If a secret is exposed, rotate it immediately.
- Use environment variables or secret managers for runtime secrets.

## Reporting bugs

Please include:
1. Expected vs actual behavior.
2. Minimal reproduction steps.
3. Relevant logs/errors.
4. Environment details (provider, model, mode, OS/runtime).

## Suggesting features

Open an issue with:
1. The user/problem context.
2. Why current behavior is insufficient.
3. A proposal and alternatives considered.
4. Expected impact on evaluation quality or developer productivity.
