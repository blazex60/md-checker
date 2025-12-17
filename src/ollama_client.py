from __future__ import annotations

import os
import requests
from typing import Any, Dict, List


def _host() -> str:
    return os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")


def _model() -> str:
    return os.getenv("OLLAMA_MODEL", "gemma2:2b")


def pull_model(model: str | None = None) -> None:
    """
    Ollama側にモデルをpullさせる（存在すれば何もしない）。
    """
    m = model or _model()
    r = requests.post(f"{_host()}/api/pull", json={"name": m}, timeout=600)
    r.raise_for_status()


def lint_with_llm(markdown_text: str) -> Dict[str, Any]:
    """
    Markdown文の「表記揺れ/固有名詞揺れ/曖昧表現」を“候補”として列挙する。
    自動修正はしない。
    """
    system = (
        "You are a strict proofreading assistant for Japanese technical Markdown.\n"
        "Return ONLY valid JSON. No prose.\n"
        "Do NOT rewrite the text. Only list candidates and hints.\n"
        "JSON schema:\n"
        "{\n"
        '  "terms": [{"surface":"...", "note":"..."}],\n'
        '  "inconsistencies": [{"type":"proper_noun|style|term", "a":"...", "b":"...", "note":"..."}],\n'
        '  "suggestions": ["..."]\n'
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
            "temperature": 0.2
        }
    }

    r = requests.post(f"{_host()}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    # Ollamaは message.content がJSON文字列で返る
    content = data["message"]["content"]
    return requests.json.loads(content) if hasattr(requests, "json") else __import__("json").loads(content)
