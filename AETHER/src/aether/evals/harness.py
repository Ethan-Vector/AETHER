from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ..agent import default_agent_from_env


@dataclass
class CaseResult:
    case_id: str
    ok: bool
    final: str
    steps: int
    tool_calls: int


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def run_case(agent, case: Dict[str, Any]) -> CaseResult:
    case_id = str(case.get("id", "unknown"))
    prompt = str(case.get("prompt", ""))
    expect_contains = str(case.get("expect_contains", "")).strip()
    expect_tool = str(case.get("expect_tool", "")).strip()

    res = agent.run(prompt)
    ok = True
    if expect_contains and expect_contains not in res.final:
        ok = False
    # Lightweight tool check via trace (if present)
    if expect_tool and res.trace_path:
        try:
            with open(res.trace_path, "r", encoding="utf-8") as f:
                used = any((json.loads(l).get("type") == "tool_ok" and json.loads(l).get("tool") == expect_tool) for l in f if l.strip())
            if not used:
                ok = False
        except Exception:
            ok = False

    return CaseResult(case_id=case_id, ok=ok, final=res.final, steps=res.steps, tool_calls=res.tool_calls)


def main(argv: Optional[List[str]] = None) -> None:
    ap = argparse.ArgumentParser(description="AETHER eval harness")
    ap.add_argument("--dataset", default="evals/datasets/smoke.jsonl")
    args = ap.parse_args(argv)

    agent = default_agent_from_env()
    cases = load_jsonl(args.dataset)

    results: List[CaseResult] = []
    t0 = time.time()
    for c in cases:
        results.append(run_case(agent, c))

    dt = time.time() - t0
    passed = sum(1 for r in results if r.ok)
    total = len(results)

    print(f"Dataset: {args.dataset}")
    print(f"Passed: {passed}/{total}  ({(passed/total*100.0) if total else 0:.1f}%)")
    print(f"Time: {dt:.2f}s")

    for r in results:
        status = "OK" if r.ok else "FAIL"
        print(f"- {status} {r.case_id} | steps={r.steps} tool_calls={r.tool_calls} | final={r.final[:80]}")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
