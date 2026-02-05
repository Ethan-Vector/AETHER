from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Iterable, Optional, Set


@dataclass(frozen=True)
class Guardrails:
    max_steps: int = 8
    max_tool_calls: int = 4
    tool_allowlist: Optional[Set[str]] = None
    workspace_dir: str = "workspace"
    tool_timeout_s: float = 3.0

    def is_tool_allowed(self, name: str) -> bool:
        if self.tool_allowlist is None:
            return True
        return name in self.tool_allowlist

    def ensure_workspace(self) -> str:
        wd = os.path.abspath(self.workspace_dir)
        os.makedirs(wd, exist_ok=True)
        return wd
