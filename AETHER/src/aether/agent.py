from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .guardrails import Guardrails
from .llm import LLMClient, StubLLM
from .tools.base import ToolContext
from .tool_registry import build_registry
from .tracing import TraceWriter
from .types import AgentResult, Message


@dataclass
class Agent:
    llm: LLMClient
    guardrails: Guardrails
    trace_writer: Optional[TraceWriter] = None

    def run(self, user_prompt: str, system_prompt: str = "You are a helpful tool-using agent.") -> AgentResult:
        registry = build_registry()
        tools_schema = registry.schema()

        workspace = self.guardrails.ensure_workspace()
        ctx = ToolContext(workspace_dir=workspace)

        messages: List[Message] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        steps = 0
        tool_calls = 0
        trace_path: Optional[str] = None
        if self.trace_writer:
            trace_path = self.trace_writer.start()
            self.trace_writer.write_event(trace_path, {
                "type": "start",
                "ts": time.time(),
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
            })

        while steps < self.guardrails.max_steps:
            steps += 1

            if self.trace_writer and trace_path:
                self.trace_writer.write_event(trace_path, {
                    "type": "llm_request",
                    "ts": time.time(),
                    "step": steps,
                    "messages": self.trace_writer.snapshot_messages(messages),
                    "tools": tools_schema,
                })

            out = self.llm.complete(messages, tools_schema=tools_schema)

            if self.trace_writer and trace_path:
                self.trace_writer.write_event(trace_path, {"type": "llm_response", "ts": time.time(), "step": steps, "output": out})

            action = out.get("action")
            if action == "final":
                final = str(out.get("final", "")).strip()
                if not final:
                    final = "(empty final)"
                if self.trace_writer and trace_path:
                    self.trace_writer.write_event(trace_path, {"type": "final", "ts": time.time(), "step": steps, "final": final})
                return AgentResult(final=final, steps=steps, tool_calls=tool_calls, trace_path=trace_path)

            if action == "tool":
                if tool_calls >= self.guardrails.max_tool_calls:
                    return AgentResult(final="Stopped: tool call budget exceeded.", steps=steps, tool_calls=tool_calls, trace_path=trace_path)

                name = str(out.get("tool_name", "")).strip()
                tool_input = out.get("tool_input") or {}
                if not isinstance(tool_input, dict):
                    tool_input = {}

                if not self.guardrails.is_tool_allowed(name):
                    obs = f"Tool '{name}' blocked by allowlist."
                    messages.append({"role": "tool", "name": name, "content": obs})
                    continue

                tool = registry.get(name)

                tool_calls += 1
                t0 = time.time()
                try:
                    # naive timeout approach: tools should be fast; for real use, run in a thread/process
                    obs = tool.run(tool_input, ctx)
                    dt = time.time() - t0
                    messages.append({"role": "tool", "name": name, "content": obs})
                    if self.trace_writer and trace_path:
                        self.trace_writer.write_event(trace_path, {"type": "tool_ok", "ts": time.time(), "step": steps, "tool": name, "dt_s": dt, "input": tool_input, "output": obs})
                except Exception as e:  # noqa: BLE001
                    dt = time.time() - t0
                    obs = f"Tool error: {type(e).__name__}: {e}"
                    messages.append({"role": "tool", "name": name, "content": obs})
                    if self.trace_writer and trace_path:
                        self.trace_writer.write_event(trace_path, {"type": "tool_err", "ts": time.time(), "step": steps, "tool": name, "dt_s": dt, "input": tool_input, "error": obs})
                continue

            # Unknown output format
            return AgentResult(final="Stopped: model returned an unknown action.", steps=steps, tool_calls=tool_calls, trace_path=trace_path)

        return AgentResult(final="Stopped: step budget exceeded.", steps=steps, tool_calls=tool_calls, trace_path=trace_path)


def default_agent_from_env() -> Agent:
    llm_name = os.getenv("AETHER_LLM", "stub").lower()
    if llm_name == "stub":
        llm: LLMClient = StubLLM()
    else:
        # Placeholder for future adapters
        llm = StubLLM()

    # allowlist from config/env; keep minimal for safety
    allow = {"calc", "note"}

    guard = Guardrails(
        max_steps=int(os.getenv("AETHER_MAX_STEPS", "8")),
        max_tool_calls=int(os.getenv("AETHER_MAX_TOOL_CALLS", "4")),
        tool_allowlist=allow,
        workspace_dir=os.getenv("AETHER_WORKSPACE", "workspace"),
    )

    trace_dir = os.getenv("AETHER_TRACE_DIR", "traces")
    tw = TraceWriter(trace_dir=trace_dir)
    return Agent(llm=llm, guardrails=guard, trace_writer=tw)
