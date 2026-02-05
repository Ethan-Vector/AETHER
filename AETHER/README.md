# AETHER

AETHER is a **reference repo** for building and shipping **tool-using AI agents** with a clean, testable architecture:
- agent loop (tool calls → observations → final)
- tool registry + guardrails (allowlist, timeouts, budget checks)
- tracing (JSONL) + lightweight eval harness
- runnable CLI + Docker + CI

> This repo ships with a **stub LLM** so it runs offline. Swap in your preferred LLM provider by implementing `LLMClient`.

## Quickstart (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
aether chat
```

Run smoke evals:

```bash
python -m aether.evals.harness
```

## Repo layout

- `src/aether/` — agent core
- `src/aether/tools/` — tool interfaces + built-ins
- `evals/` — datasets (JSONL)
- `docs/` — architecture + extension guides
- `examples/` — minimal end-to-end scripts
- `.github/workflows/ci.yml` — ruff + pytest + smoke evals

## What to customize first

1. Replace the stub LLM (`aether.llm.StubLLM`) with a real provider client.
2. Add domain tools in `src/aether/tools/` and register them in `tool_registry.py`.
3. Expand `evals/datasets/*.jsonl` with real tasks + expected properties.

## Safety note

This repo is designed for **bounded, allowlisted tool use**. By default:
- only built-in safe tools are enabled
- any network access tool is a stub
- file operations are scoped to `./workspace/`

See `docs/guardrails.md`.
