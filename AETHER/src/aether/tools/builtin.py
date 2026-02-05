from __future__ import annotations

import ast
import operator as op
from dataclasses import dataclass
from typing import Any, Dict

from .base import ToolContext

_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.Mod: op.mod,
}

def _safe_eval(expr: str) -> float:
    def _eval(node):
        if isinstance(node, ast.Num):  # type: ignore[attr-defined]
            return node.n
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp):
            if type(node.op) not in _ALLOWED_OPS:
                raise ValueError("Operator not allowed")
            return _ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in _ALLOWED_OPS:
                raise ValueError("Operator not allowed")
            return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
        raise ValueError("Expression not allowed")

    tree = ast.parse(expr, mode="eval")
    return float(_eval(tree.body))  # type: ignore[arg-type]


@dataclass
class CalcTool:
    name: str = "calc"
    description: str = "Safely evaluate basic arithmetic expressions (no variables, no functions)."

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
            "additionalProperties": False,
        }

    def run(self, tool_input: Dict[str, Any], ctx: ToolContext) -> str:
        expr = str(tool_input.get("expression", "")).strip()
        if len(expr) > 200:
            raise ValueError("Expression too long")
        value = _safe_eval(expr)
        # normalize -0.0
        if abs(value) == 0.0:
            value = 0.0
        return str(value)


@dataclass
class NoteTool:
    name: str = "note"
    description: str = "Store a short note in the workspace (append-only)."

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        }

    def run(self, tool_input: Dict[str, Any], ctx: ToolContext) -> str:
        text = str(tool_input.get("text", "")).strip()
        if not text:
            raise ValueError("Empty note")
        if len(text) > 5000:
            raise ValueError("Note too long")
        import os
        path = os.path.join(ctx.workspace_dir, "notes.txt")
        with open(path, "a", encoding="utf-8") as f:
            f.write(text.replace("\r", "") + "\n")
        return f"Saved note ({len(text)} chars) to workspace/notes.txt"
