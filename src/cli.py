from __future__ import annotations

import argparse
import os
from pathlib import Path

# 相対インポート
from ollama_client import pull_model, lint_with_llm
from rules import lint_with_rules

def print_analysis(advice: dict, source: str = "LLM") -> None:
    """解析結果を表示する"""
    
    title = f" 🔍 解析レポート ({source}) "
    print("\n" + title.center(60, "="))

    # --- ルールベースの結果 ---
    rule_issues = advice.get("rule_based_issues", [])
    if rule_issues:
        print("\n[基本的なフォーマットの問題]")
        for issue in rule_issues:
            print(f" • {issue}")
    elif source == "Rules":
        print("\n[基本的なフォーマットの問題]\n (問題は見つかりませんでした)")

    # --- LLMの結果 ---
    
    # 用語・固有名詞
    terms = advice.get("terms", [])
    if terms:
        print("\n[用語 / 固有名詞]")
        for t in terms:
            surface = t.get("surface", "???")
            note = t.get("note", "")
            print(f" • {surface:<20} | {note}")

    # 表記揺れ
    inconsistencies = advice.get("inconsistencies", [])
    if inconsistencies:
        print("\n[表記揺れ]")
        for i in inconsistencies:
            a = i.get("a", "?")
            b = i.get("b", "?")
            note = i.get("note", "")
            itype = i.get("type", "style")
            print(f" • {a} <-> {b} ({itype})\n   └─ {note}")

    # 提案
    suggestions = advice.get("suggestions", [])
    if suggestions:
        print("\n[AIによる提案]")
        for s in suggestions:
            print(f" • {s}")

    print("\n" + "="*60 + "\n")


def process_file(file_path: Path, use_llm: bool) -> None:
    """単一ファイルの処理"""
    print(f"チェック中: {file_path}")
    
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return

    # 1. ルールベース (常に実行)
    rule_result = lint_with_rules(text)
    print_analysis(rule_result, source="ルール")

    # 2. LLM (オプション)
    if use_llm:
        print("LLMの応答を待機中...")
        try:
            advice = lint_with_llm(text[:1500])
            print_analysis(advice, source="AI (Ollama)")
        except Exception as e:
            print(f"LLMエラー: {e}")
            print("(Ollamaが起動しているか、モデルがpullされているか確認してください)")
    else:
        print("  -> AIチェックはスキップされました。 --llm で有効化できます。")
        print()


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="mdcheck")
    p.add_argument("path", nargs="?", help="Markdownファイルまたはディレクトリのパス")
    p.add_argument("--llm", action="store_true", help="OllamaによるAIアドバイスを有効化")
    p.add_argument("--pull-model", action="store_true", help="Ollamaモデルをpullして終了")
    p.add_argument("--gui", action="store_true", help="GUIモードで起動")
    args = p.parse_args(argv)

    if args.pull_model:
        pull_model()
        print(f"[OK] モデルをpullしました: {os.getenv('OLLAMA_MODEL', 'gemma2:2b')}")
        return
    
    if args.gui:
        from gui import main as gui_main
        gui_main()
        return

    if not args.path:
        p.print_help()
        raise SystemExit(1)

    target_path = Path(args.path)

    if not target_path.exists():
        raise SystemExit(f"パスが見つかりません: {target_path}")

    if target_path.is_dir():
        md_files = list(target_path.glob("*.md"))
        if not md_files:
            print(f"{target_path} にMarkdownファイルが見つかりませんでした")
            return
            
        print(f"{target_path} 内に {len(md_files)} 個のMarkdownファイルが見つかりました\n")
        for md_file in md_files:
            process_file(md_file, args.llm)
            
    elif target_path.is_file():
        process_file(target_path, args.llm)
        
    else:
        print(f"エラー: {target_path} は有効なファイルまたはディレクトリではありません")


if __name__ == "__main__":
    main()