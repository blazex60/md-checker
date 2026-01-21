#!/bin/bash
# ヘッドレス環境でGUIをテストする場合

export QT_QPA_PLATFORM=offscreen
cd "$(dirname "$0")"

echo "🚀 MDCheck GUI (オフスクリーンモード) を起動します..."
echo "注: このモードでは画面表示はされませんが、動作確認できます"
echo ""

uv run python src/gui.py
