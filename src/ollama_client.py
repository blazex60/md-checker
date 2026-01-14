from __future__ import annotations

import os
import requests
import json
from typing import Any, Dict
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

def _host() -> str:
    return os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")


def _model() -> str:
    return os.getenv("OLLAMA_MODEL", "gemma2:2b")


def pull_model(model: str | None = None) -> None:
    """
    Ollama側にモデルをpullさせる
    """
    m = model or _model()
    # モデルの有無確認は省略し、常にpullリクエストを投げる（既ににあれば高速に終わる）
    print(f"Pulling model: {m} ...")
    r = requests.post(f"{_host()}/api/pull", json={"name": m}, stream=True, timeout=600)
    # stream=Trueにしているので、レスポンスを待つ
    for line in r.iter_lines():
        if line:
            # 進行状況が見たい場合はここでデコードしてprintしても良い
            pass
    if r.status_code != 200:
        raise ValueError(f"Failed to pull model: {r.text}")


def lint_with_llm(markdown_text: str) -> Dict[str, Any]:
    """
    Markdown文の「表記揺れ/固有名詞揺れ/曖昧表現」を“候補”として列挙する。
    """
    # プロンプトを日本語出力指示付きに変更
    system = (
        "You are a strict proofreading assistant for Japanese technical Markdown.\n"
        "Return ONLY valid JSON. No prose.\n"
        "Do NOT rewrite the text. Only list candidates and hints.\n"
        "IMPORTANT: The values for 'note' and 'suggestions' MUST be in **Japanese**.\n"
        "JSON schema:\n"
        "{\n"
        '  "terms": [{"surface":"...", "note":"(Japanese explanation)"}],\n'
        '  "inconsistencies": [{"type":"proper_noun|style|term", "a":"...", "b":"...", "note":"(Japanese explanation)"}],\n'
        '  "suggestions": ["(Japanese suggestion)..."]\n'
        "}\n"
    )

    user = (
        "Analyze the following Markdown and list:\n"
        "- proper nouns / product names / acronyms candidates\n"
        "- possible spelling inconsistencies\n"
        "- short suggestions (max 5)\n\n"
        "Markdown:\n"
        "-----\n"
        f"{markdown_text}\n"
        "-----\n"
    )

    payload = {
        "model": _model(),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1 # 安定性を高めるため少し下げる
        }
    }

    r = requests.post(f"{_host()}/api/chat", json=payload, timeout=120)
    if r.status_code != 200:
        raise ValueError(f"Ollama API Error ({r.status_code}): {r.text}")
    
    data = r.json()
    content = data["message"]["content"]
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # 万が一JSON以外が返ってきた場合のフォールバック（簡易）
        return {"suggestions": ["JSON解析エラー: LLMの応答が不正でした"]}