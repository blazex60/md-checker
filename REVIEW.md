# コードレビュー結果 / Code Review Report

**レビュー日時 / Review Date:** 2026-01-28  
**プロジェクト / Project:** mdcheck - Markdown checker with AI assistance  
**レビュー範囲 / Review Scope:** 全リポジトリのコード品質、セキュリティ、設計パターンの評価

---

## 🔴 クリティカル / Critical Issues

### 1. パッケージインポート設定の不一致
**ファイル:** `pyproject.toml:22-23`, `src/cli.py:8-9`, `src/gui.py:29-30`  
**深刻度:** クリティカル  
**問題点:**
- `pyproject.toml` のエントリーポイントが `mdcheck.cli:main` と `mdcheck.gui:main` を指定しているが、ソースコードは相対インポート（`from ollama_client import ...`）を使用している
- インストール後、コマンド実行時に `ModuleNotFoundError` が発生する

**証拠:**
```python
# pyproject.toml line 22
mdcheck = "mdcheck.cli:main"  # expects mdcheck/cli.py

# src/cli.py line 8
from ollama_client import pull_model  # relative import without package prefix
```

**推奨される修正:**
以下のいずれかを実施：
1. インポートをパッケージ相対インポートに変更: `from mdcheck.ollama_client import ...`
2. `src` ディレクトリを `mdcheck` にリネームして、絶対パッケージインポートに更新
3. `pyproject.toml` のスクリプトを `mdcheck.src.cli:main` に変更

**影響範囲:**
- CLI実行 (`mdcheck`)
- GUI実行 (`mdcheck-gui`)
- 全てのインストール後の実行が失敗する

---

## 🟠 高優先度 / High Priority Issues

### 2. 不完全な __init__.py がパッケージ機能を阻害
**ファイル:** `src/__init__.py:1-6`  
**深刻度:** 高  
**問題点:**
- `__init__.py` に他プロジェクトのプレースホルダーコード（"Hello from interactive-novel!"）が残っている
- パッケージの実際の機能をエクスポートしていない
- `from mdcheck import ...` 形式のインポートが不可能

**推奨される修正:**
```python
from mdcheck.rules import lint_with_rules
from mdcheck.ollama_client import lint_with_llm, pull_model

__all__ = ["lint_with_rules", "lint_with_llm", "pull_model"]
```

---

## 🟡 中優先度 / Medium Priority Issues

### 3. ストリーミングAPIコールでの潜在的レスポンスボム
**ファイル:** `src/ollama_client.py:27-33`  
**深刻度:** 中  
**問題点:**
- `pull_model()` 関数が `stream=True` を使用し、`r.iter_lines()` で全行を反復処理するが何もしない
- Ollamaサーバーが巨大または無限ストリームを送信した場合、無制限のメモリ消費やハングアップの可能性がある

**推奨される修正:**
```python
max_iterations = 10000
for i, line in enumerate(r.iter_lines()):
    if i >= max_iterations:
        break
    if line:
        # Optional: decode and print progress
        data = json.loads(line)
        if data.get("status") == "success":
            break
```

---

### 4. JSONパース前のステータスコードチェック漏れ
**ファイル:** `src/ollama_client.py:27-34`  
**深刻度:** 中  
**問題点:**
- `pull_model()` でステータスコードチェックがストリーム全体の反復処理後に実施される
- エラーステータスコードでも全レスポンス本文を処理してしまう

**推奨される修正:**
```python
r = requests.post(f"{_host()}/api/pull", json={"name": m}, stream=True, timeout=600)
r.raise_for_status()  # Check immediately
for line in r.iter_lines():
    # ...
```

---

### 5. 広範囲の例外キャッチが実際のエラーを隠蔽
**ファイル:** `src/cli.py:64-66, 78-80`; `src/gui.py:338-339, 369-370, 432-434`  
**深刻度:** 中  
**問題点:**
- 複数箇所で `except Exception as e` を使用し、システムエラーを含む全ての例外をキャッチ
- デバッグが困難になり、深刻な問題（メモリ不足、プログラミングバグ）を隠す可能性がある

**推奨される修正:**
```python
# Before
except Exception as e:
    print(f"エラー: {e}")

# After - be specific
except (IOError, UnicodeDecodeError) as e:
    print(f"ファイル読み込みエラー: {e}")
except requests.RequestException as e:
    print(f"LLMエラー: {e}")
```

---

### 6. 警告なしのテキスト切り詰め
**ファイル:** `src/cli.py:76`, `src/gui.py:407`  
**深刻度:** 中  
**問題点:**
- LLMに送信前、テキストを1500文字に暗黙的に切り詰め（`text[:1500]`）
- ユーザーへの警告なし、設定不可
- 切り詰められた部分の問題を見逃す可能性

**推奨される修正:**
```python
MAX_LLM_TEXT_LENGTH = int(os.getenv("MAX_LLM_TEXT_LENGTH", "1500"))
text_to_analyze = text[:MAX_LLM_TEXT_LENGTH]
if len(text) > MAX_LLM_TEXT_LENGTH:
    print(f"⚠️  警告: テキストが長すぎるため、最初の{MAX_LLM_TEXT_LENGTH}文字のみを解析します")
advice = lint_with_llm(text_to_analyze)
```

---

### 7. ユーザー提供URLの検証不足
**ファイル:** `src/ollama_client.py:13`  
**深刻度:** 中  
**問題点:**
- `OLLAMA_HOST` 環境変数が検証なしで直接HTTPリクエストに使用される
- サーバーコンテキストでの使用時、SSRF（Server-Side Request Forgery）やその他の問題を引き起こす可能性

**推奨される修正:**
```python
def _host() -> str:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    # Validate URL
    from urllib.parse import urlparse
    parsed = urlparse(host)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid OLLAMA_HOST scheme: {parsed.scheme}")
    return host
```

---

## 🔵 低優先度 / Low Priority Issues

### 8. デバウンス処理での競合状態
**ファイル:** `src/gui.py:44-53`  
**深刻度:** 低  
**問題点:**
- テキスト変更のたびにタイマーを停止・再起動するが、正しいテキストバージョンが処理される保証がない
- ユーザーが500msウィンドウ中に編集を続けた場合、古いバージョンが処理される可能性

**備考:** プレビュー機能としては許容範囲だが、本番コードではテキストコンテンツのキャプチャを検討

---

### 9. JSONデコードフォールバックでのエラーハンドリング不足
**ファイル:** `src/ollama_client.py:86-90`  
**深刻度:** 低  
**問題点:**
- JSONパース失敗時、`suggestions` キーのみを持つ辞書を返す
- 呼び出し側コードは `terms`、`inconsistencies`、`suggestions` の3つのキーを期待

**推奨される修正:**
```python
except json.JSONDecodeError:
    return {
        "terms": [],
        "inconsistencies": [],
        "suggestions": ["JSON解析エラー: LLMの応答が不正でした"]
    }
```

---

## ✅ 良好な点 / Positive Aspects

1. **明確な責任分離:**
   - `rules.py`: ルールベースチェック
   - `ollama_client.py`: LLM連携
   - `cli.py` / `gui.py`: インターフェース

2. **環境設定の柔軟性:**
   - `.env` ファイルと環境変数による設定
   - デフォルト値の適切な設定

3. **ユーザーフレンドリーな日本語出力:**
   - エラーメッセージと結果が日本語で表示
   - 技術的でない日本語ユーザーにも理解しやすい

4. **タイムアウト設定:**
   - Ollamaへのリクエストに適切なタイムアウトを設定（120秒、600秒）

5. **JSONフォーマット指定:**
   - LLMレスポンスに `"format": "json"` を指定し、構造化された出力を確保

---

## 📊 セキュリティスキャン結果 / Security Scan

依存パッケージのセキュリティチェックを推奨：
- `requests`: HTTPリクエストライブラリ - 最新版を使用することを推奨
- `PySide6`: 大規模なGUIフレームワーク - 定期的な更新が必要
- `pygments`: コードハイライト - XSS脆弱性の履歴あり、最新版を確認

---

## 🎯 優先度別推奨事項 / Recommended Actions by Priority

### 最優先（即座に対応）
1. ✅ パッケージインポート設定の修正
2. ✅ `__init__.py` の適切な実装

### 高優先度（次のリリース前）
3. 例外ハンドリングの具体化
4. テキスト切り詰めの警告追加
5. URL検証の実装

### 中優先度（機能改善時）
6. ストリーミングAPIの制限追加
7. ステータスコードチェックの前倒し
8. JSONフォールバックの完全化

---

## 📝 総評 / Overall Assessment

**コード品質:** ⭐⭐⭐☆☆ (3/5)  
**セキュリティ:** ⭐⭐⭐☆☆ (3/5)  
**保守性:** ⭐⭐⭐⭐☆ (4/5)  
**ドキュメント:** ⭐⭐⭐⭐☆ (4/5)

このプロジェクトは明確な目的を持ち、適切に構造化されています。READMEは詳細で分かりやすく、コードも比較的読みやすい構造になっています。ただし、クリティカルなパッケージ設定の問題があり、現状ではインストール後の実行が不可能です。この問題を修正し、例外ハンドリングを改善すれば、実用的なツールとして十分に機能します。

---

**レビュアー:** GitHub Copilot Code Review Agent  
**レビューツール:** 静的解析 + 手動コードレビュー
