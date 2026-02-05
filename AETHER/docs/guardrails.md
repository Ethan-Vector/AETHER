# Guardrails

AETHER enforces guardrails at the boundary between model and tools.

## What is enforced

- Tool allowlist
- Max agent steps
- Max tool calls
- Workspace scoping for file operations (when you add them)
- Timeout for tool execution

## Why

Most "agent incidents" are:
- infinite loops
- unbounded tool spam
- tool misuse (wrong tool, wrong args)
- unsafe side effects

Budgets + allowlists are the cheapest insurance.
