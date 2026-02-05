from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol


@dataclass
class ToolContext:
    workspace_dir: str


class Tool(Protocol):
    name: str
    description: str

    def input_schema(self) -> Dict[str, Any]:
        ...

    def run(self, tool_input: Dict[str, Any], ctx: ToolContext) -> str:
        ...
