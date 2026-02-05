from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .base import Tool
from .builtin import CalcTool, NoteTool


@dataclass
class ToolRegistry:
    tools: Dict[str, Tool]

    @classmethod
    def default(cls) -> "ToolRegistry":
        t: Dict[str, Tool] = {x.name: x for x in [CalcTool(), NoteTool()]}
        return cls(tools=t)

    def get(self, name: str) -> Tool:
        if name not in self.tools:
            raise KeyError(f"Unknown tool: {name}")
        return self.tools[name]

    def schema(self) -> Dict[str, Any]:
        # A generic "tools schema" representation that real LLM adapters can map to their format
        return {
            name: {
                "description": getattr(tool, "description", ""),
                "input_schema": tool.input_schema(),
            }
            for name, tool in self.tools.items()
        }
