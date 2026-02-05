# INSTRUCTIONS

This file is the "operator manual" for AETHER.

## 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 2) Run the interactive chat

```bash
aether chat
```

The CLI uses a **stub LLM** that demonstrates tool calling.  
To connect a real model, implement `LLMClient` in `src/aether/llm.py` and set `AETHER_LLM=your_client_name`.

## 3) Add a new tool

1. Create a tool class in `src/aether/tools/` implementing the `Tool` protocol.
2. Register it in `src/aether/tool_registry.py`.
3. Add it to the allowlist in `configs/aether.yaml`.
4. Add a test under `tests/`.

See `docs/adding_tools.md`.

## 4) Evals workflow

- Add tasks to `evals/datasets/smoke.jsonl`
- Run:

```bash
python -m aether.evals.harness --dataset evals/datasets/smoke.jsonl
```

The harness outputs:
- pass/fail
- tool usage sanity checks
- latency/steps summary
- traces in `./traces/`

## 5) Docker

```bash
docker build -t aether .
docker run --rm -it aether aether chat
```
