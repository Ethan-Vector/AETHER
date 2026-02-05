from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, TypedDict

Role = Literal["system", "user", "assistant", "tool"]

class Message(TypedDict, total=False):
    role: Role
    content: str
    name: str  # for tool messages

class ToolCall(TypedDict):
    tool_name: str
    tool_input: Dict[str, Any]

@dataclass
class AgentResult:
    final: str
    steps: int
    tool_calls: int
    trace_path: Optional[str] = None
