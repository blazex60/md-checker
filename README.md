# mdcheck

`mdcheck` は、Markdown文書の品質を高めるためのツールです。
基本的なフォーマットミスの検出を行う「ルールベースチェック」と、ローカルLLM（Ollama）を使用した「AI校正・アドバイス」の2つの機能を備えています。
CLI（コマンドライン）とGUI（グラフィカルインターフェース）の両方で利用可能です。

## 特徴

### 2つの実行モード
- **CLI**: コマンドラインでの一括チェック・CI/CD連携に最適
- **GUI**: リアルタイムプレビュー付きのMarkdownエディタ（Mermaid対応）

### 1. ルールベースチェック（高速・常時実行）
Pythonによる静的解析で、以下の問題を瞬時に検出します。
- **見出しのフォーマット**: `#` の後にスペースがないもの（例: `#Title`）を検出
- **行末の余計な空白**: 不要なスペースやタブの混入を警告
- **TODOコメント**: 残ったままの `TODO` や `FIXME` を検出

### 2. AI校正（オプション・ローカルLLM）
Ollamaを経由してローカルLLMを使用し、文脈に応じたアドバイスを提供します。
- **用語・固有名詞の抽出**: 文書内の重要なキーワードをリストアップ
- **表記揺れの検出**: （例: `サーバー` <-> `サーバ`、`mdcheck` <-> `MDChecker` など）
- **改善提案**: 文章の分かりにくい点やスタイルに関する具体的なアドバイス（日本語で出力）

## 必要要件

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) または pip（パッケージ管理）
- [Ollama](https://ollama.com/) (AI機能を使用する場合)

## インストール

このリポジトリをクローンし、`uv` または `pip` を使用してインストールします。

```bash
# クローン
git clone <repository-url>
cd mdcheck

# uvの場合（推奨）
uv pip install -e .

# pipの場合
pip install -e .
```

## 使い方

### CLIモード

#### 基本的なチェック
ファイルパス、またはディレクトリパスを指定して実行します。
ディレクトリを指定した場合、その中の `.md` ファイルすべてをチェックします。

```bash
# 単一ファイル
mdcheck README.md

# ディレクトリ一括
mdcheck docs/
```

実行結果には、フォーマットの問題点が表示されます。

#### AIアドバイスの有効化 (`--llm`)
`--llm` オプションを付けると、ルールベースチェックの後にAIによる解析が実行されます。
※ 事前にOllamaを起動しておく必要があります。

```bash
mdcheck README.md --llm
```

#### モデルの準備 (`--pull-model`)
デフォルトで使用するモデル（`gemma2:2b`）がローカルにない場合、以下のコマンドでダウンロードできます。

```bash
mdcheck --pull-model
```

### GUIモード

GUIモードでは、Markdownエディタ、リアルタイムプレビュー、問題検出パネルが統合された環境で作業できます。

#### 起動方法

```bash
# コマンドで起動
mdcheck-gui

# または起動スクリプトを使用
./run-gui.sh
```

#### 主な機能

- **3ペイン構成**: エディタ、プレビュー、問題リスト
- **リアルタイムプレビュー**: 入力から500ms後に自動更新（Mermaid図表対応）
- **シンタックスハイライト**: コードブロックの色付け表示
- **問題の自動検出**: ルールチェック（F5）とAIチェック（F6）
- **行ジャンプ機能**: 問題リストの項目をクリックすると該当行に移動
- **見やすい色設定**: AIチェック（ライトブルー）、ルールチェック（ライトレッド）

#### キーボードショートカット

| キー | 機能 |
| --- | --- |
| `Ctrl+O` | ファイルを開く |
| `Ctrl+S` | 保存 |
| `Ctrl+Shift+S` | 名前を付けて保存 |
| `F5` | ルールチェック実行 |
| `F6` | AIチェック実行 |
| `F7` | 全チェック実行（ルール+AI） |
| `Ctrl+Q` | 終了 |

#### ヘッドレス環境での実行

サーバー環境などでテストする場合：

```bash
./run-gui-headless.sh
```

## 設定

環境変数を使用することで、Ollamaの接続先や使用モデルを変更できます。`.env` ファイルに記述することも可能です。

| 環境変数 | デフォルト値 | 説明 |
| --- | --- | --- |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollamaサーバーのアドレス |
| `OLLAMA_MODEL` | `gemma2:2b` | 使用するLLMモデル |

**設定例 (.env):**
```ini
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
```

## プロジェクト構成

```
mdcheck/
├── src/                    # ソースコード
│   ├── cli.py             # CLIエントリーポイント
│   ├── gui.py             # GUIアプリケーション
│   ├── rules.py           # ルールベースのチェック処理
│   └── ollama_client.py   # Ollama API連携
├── docs/                   # ドキュメント
├── sample.md              # サンプルファイル
├── run-gui.sh             # GUI起動スクリプト
├── run-gui-headless.sh    # ヘッドレス環境用
├── pyproject.toml         # プロジェクト設定
└── README.md              # このファイル
```

## 開発

### 依存パッケージ

- **requests**: Ollama APIとの通信
- **python-dotenv**: 環境変数管理
- **PySide6**: GUI実装（Qt for Python）
- **markdown**: Markdown → HTML変換
- **pymdown-extensions**: Markdown拡張機能（Mermaid等）
- **pygments**: シンタックスハイライト

### 実行コマンド

```bash
# CLI（開発モード）
uv run python src/cli.py sample.md --llm

# GUI（開発モード）
uv run python src/gui.py
```

## ライセンス

[MIT License](LICENSE)