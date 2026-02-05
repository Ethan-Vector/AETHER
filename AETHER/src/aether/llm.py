from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from .types import Message

# The model output is normalized into one of:
# - {"action": "tool", "tool_name": "...", "tool_input": {...}}
# - {"action": "final", "final": "..."}

class LLMClient(Protocol):
    name: str

    def complete(self, messages: List[Message], tools_schema: Dict[str, Any]) -> Dict[str, Any]:
        ...


@dataclass
class StubLLM:
    """Offline demo LLM.

    It uses simple heuristics:
    - If the user asks to calculate an expression, it emits a tool call to `calc`.
    - If the user says "note:", it stores a note via `note`.
    Otherwise it returns a short final answer.

    The point is to validate the plumbing (tool loop, tracing, guardrails),
    not to be smart.
    """

    name: str = "stub"

    _calc_pat = re.compile(r"(?:calc|calculate|compute)\s*[:]?\s*(.+)$", re.IGNORECASE)
    _note_pat = re.compile(r"(?:note|memo)\s*[:]?\s*(.+)$", re.IGNORECASE)

    def complete(self, messages: List[Message], tools_schema: Dict[str, Any]) -> Dict[str, Any]:
        last_user = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        text = (last_user.get("content") if last_user else "") or ""
        m = self._calc_pat.search(text.strip())
        if m:
            expr = m.group(1).strip()
            return {"action": "tool", "tool_name": "calc", "tool_input": {"expression": expr}}

        m = self._note_pat.search(text.strip())
        if m:
            note = m.group(1).strip()
            return {"action": "tool", "tool_name": "note", "tool_input": {"text": note}}

        # If a tool just ran, acknowledge it.
        last_tool = next((m for m in reversed(messages) if m.get("role") == "tool"), None)
        if last_tool and last_tool.get("content"):
            return {"action": "final", "final": f"Got it. Tool output: {last_tool['content']}"}

        return {"action": "final", "final": "I’m the AETHER stub LLM. Try: `calculate: 2*(3+4)` or `note: buy milk`."}
