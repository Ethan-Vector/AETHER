# Adding tools

A tool in AETHER is:
- a name (`calc`)
- an input schema (simple JSON schema dict)
- a `run(input, ctx)` method that returns a **string** observation

## Steps

1. Add a file under `src/aether/tools/` (or extend `builtin.py`)
2. Register in `src/aether/tool_registry.py`
3. Update `configs/aether.yaml` allowlist
4. Add tests in `tests/test_tools.py`
5. Add at least one eval case in `evals/datasets/smoke.jsonl`

## Design rules

- Keep tools **side-effect bounded**.
- If you need files: use the provided `workspace_dir` and never escape it.
- Never trust tool input: validate types and sizes.
