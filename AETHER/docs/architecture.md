# Architecture

AETHER is deliberately small. The goal is to keep the agent **inspectable**.

## Core loop

1. Build a `Conversation` (system + user + tool observations)
2. Call `LLMClient.complete(messages, tools_schema)`
3. If the model returns `action=tool`:
   - validate tool name against allowlist
   - run tool with timeout
   - append observation
4. If the model returns `action=final`: stop.

## Components

- `aether.agent.Agent`: orchestrates the loop, budgets, and stop conditions
- `aether.tools`: tool protocol, registry, built-ins
- `aether.guardrails.Guardrails`: allowlist + budgets + workspace scoping
- `aether.tracing.TraceWriter`: writes JSONL traces for debugging and evals
- `aether.evals.harness`: runs datasets and checks outcomes

## Why this shape works

- Deterministic tools, non-deterministic model — the loop keeps them separated.
- Tool calls are explicit and auditable (trace file).
- Budgets force you to design for cost/latency from day one.
