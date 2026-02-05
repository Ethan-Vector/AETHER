# Contributing

## Local checks

```bash
pip install -e ".[dev]"
ruff check .
pytest
python -m aether.evals.harness
```

## Guidelines
- Keep tools deterministic and side-effect bounded.
- Prefer small interfaces and pure functions.
- Add tests for new tools and new failure modes.
