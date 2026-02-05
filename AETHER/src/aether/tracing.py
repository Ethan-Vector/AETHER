from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from .types import Message


@dataclass
class TraceWriter:
    trace_dir: str = "traces"

    def start(self) -> str:
        os.makedirs(self.trace_dir, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        path = os.path.join(self.trace_dir, f"aether-trace-{ts}.jsonl")
        # Touch file
        with open(path, "a", encoding="utf-8"):
            pass
        return path

    def write_event(self, path: str, event: Dict[str, Any]) -> None:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def snapshot_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        # drop large fields if needed in future
        return [dict(m) for m in messages]
