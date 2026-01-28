#!/bin/bash
# MDCheck GUI起動スクリプト

cd "$(dirname "$0")"

echo "🚀 MDCheck GUIを起動します..."
echo ""
echo "使い方:"
echo "  1. File > Open でMarkdownファイルを開く"
echo "  2. エディタで編集すると、プレビューが自動更新されます"
echo "  3. Check > Run Rules Check (F5) でルールチェック"
echo "  4. Check > Run AI Check (F6) でAIチェック（Ollama必要）"
echo "  5. 問題リストの項目をクリックすると、該当行にジャンプします"
echo ""
echo "サンプルファイル: sample.md"
echo ""

uv run python -m mdcheck.gui
