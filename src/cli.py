from __future__ import annotations

import argparse
import os
import json
from pathlib import Path

# パッケージ内のモジュールをインポート
# 実行時は 'mdcheck' コマンド、または 'python -m src.mdcheck.cli' などで呼び出します
from ollama_client import pull_model, lint_with_llm
from rules import lint_with_rules  # <--- 追加

def print_analysis(advice: dict, source: str = "LLM") -> None:
    """解析結果を表示するヘルパー関数"""
    
    # タイトル表示
    title = f" 🔍 Analysis Report ({source}) "
    print("\n" + title.center(60, "="))

    # --- Rule Based Issues (ルールベースの結果用) ---
    rule_issues = advice.get("rule_based_issues", [])
    if rule_issues:
        print("\n[Basic Formatting Issues]")
        for issue in rule_issues:
            print(f" • {issue}")
    elif source == "Rules":
        print("\n[Basic Formatting Issues]\n (No issues found)")

    # --- LLM Based Results (LLMの結果用) ---
    
    # Terms
    terms = advice.get("terms", [])
    if terms:
        print("\n[Terms / Proper Nouns]")
        for t in terms:
            surface = t.get("surface", "???")
            note = t.get("note", "")
            print(f" • {surface:<20} | {note}")

    # Inconsistencies
    inconsistencies = advice.get("inconsistencies", [])
    if inconsistencies:
        print("\n[Inconsistencies]")
        for i in inconsistencies:
            a = i.get("a", "?")
            b = i.get("b", "?")
            note = i.get("note", "")
            itype = i.get("type", "style")
            print(f" • {a} <-> {b} ({itype})\n   └─ {note}")

    # Suggestions
    suggestions = advice.get("suggestions", [])
    if suggestions:
        print("\n[AI Suggestions]")
        for s in suggestions:
            print(f" • {s}")

    print("\n" + "="*60 + "\n")


def process_file(file_path: Path, use_llm: bool) -> None:
    """単一ファイルの処理"""
    print(f"Checking: {file_path}")
    
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # 【変更点】
    # 1. まずルールベースのチェックを実行（常に実行される）
    rule_result = lint_with_rules(text)
    print_analysis(rule_result, source="Rules")

    # 2. --llm オプションがある場合のみ、追加でLLMチェックを実行
    if use_llm:
        print("Waiting for LLM response...")
        try:
            # 入力上限は一旦1500文字
            advice = lint_with_llm(text[:1500])
            print_analysis(advice, source="AI (Ollama)")
        except Exception as e:
            print(f"LLM Error: {e}")
            print("(Ensure Ollama is running and model is pulled)")
    else:
        # LLMが無効な場合のメッセージ（改行調整済み）
        print("  -> AI check is skipped. Use --llm to enable.")
        print()


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="mdcheck")
    p.add_argument("path", nargs="?", help="Markdown file or directory path")
    p.add_argument("--llm", action="store_true", help="Enable LLM advice via Ollama")
    p.add_argument("--pull-model", action="store_true", help="Pull Ollama model and exit")
    args = p.parse_args(argv)

    if args.pull_model:
        pull_model()
        print(f"[OK] pulled model: {os.getenv('OLLAMA_MODEL', 'gemma2:2b')}")
        return

    if not args.path:
        p.print_help()
        raise SystemExit(1)

    target_path = Path(args.path)

    if not target_path.exists():
        raise SystemExit(f"Path not found: {target_path}")

    if target_path.is_dir():
        md_files = list(target_path.glob("*.md"))
        if not md_files:
            print(f"No markdown files found in {target_path}")
            return
            
        print(f"Found {len(md_files)} markdown files in {target_path}\n")
        for md_file in md_files:
            process_file(md_file, args.llm)
            
    elif target_path.is_file():
        process_file(target_path, args.llm)
        
    else:
        print(f"Error: {target_path} is not a valid file or directory")


if __name__ == "__main__":
    main()