from __future__ import annotations

import argparse
import sys

from .agent import default_agent_from_env


def cmd_chat() -> int:
    agent = default_agent_from_env()
    print("AETHER interactive chat (type 'exit' to quit).")
    while True:
        try:
            prompt = input("\nYou> ").strip()
        except EOFError:
            print()
            return 0
        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            return 0
        res = agent.run(prompt)
        print(f"\nAether> {res.final}")
        if res.trace_path:
            print(f"(trace: {res.trace_path})")


def cmd_run(prompt: str) -> int:
    agent = default_agent_from_env()
    res = agent.run(prompt)
    print(res.final)
    if res.trace_path:
        print(res.trace_path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="aether", description="AETHER tool-using agent reference repo")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("chat", help="Interactive chat")

    r = sub.add_parser("run", help="Run a single prompt")
    r.add_argument("--prompt", required=True)
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.cmd == "chat":
        raise SystemExit(cmd_chat())
    if args.cmd == "run":
        raise SystemExit(cmd_run(args.prompt))
    raise SystemExit(2)


if __name__ == "__main__":
    main()
