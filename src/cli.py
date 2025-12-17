from __future__ import annotations

import argparse
import os
from pathlib import Path

from .ollama_client import pull_model, lint_with_llm


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="mdcheck")
    p.add_argument("file", nargs="?", help="Markdown file path")
    p.add_argument("--llm", action="store_true", help="Enable LLM advice via Ollama")
    p.add_argument("--pull-model", action="store_true", help="Pull Ollama model and exit")
    args = p.parse_args(argv)

    if args.pull_model:
        pull_model()
        print(f"[OK] pulled model: {os.getenv('OLLAMA_MODEL', 'gemma2:2b')}")
        return

    if not args.file:
        raise SystemExit("file is required (e.g., mdcheck README.md --llm)")

    text = Path(args.file).read_text(encoding="utf-8")

    if args.llm:
        advice = lint_with_llm(text[:1500])  # 入力上限（伸ばしたいなら後で）
        print(advice)
    else:
        print("LLM is disabled. (Add --llm)")


if __name__ == "__main__":
    main()
