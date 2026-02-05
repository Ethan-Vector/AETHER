from __future__ import annotations

import os
from typing import Any, Dict, Set

from .tools.registry import ToolRegistry


def load_allowlist_from_env_or_default(default: Set[str]) -> Set[str]:
    env = os.getenv("AETHER_TOOLS")
    if not env:
        return default
    return {x.strip() for x in env.split(",") if x.strip()}


def build_registry() -> ToolRegistry:
    return ToolRegistry.default()
