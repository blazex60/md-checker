from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWebEngineWidgets import QWebEngineView

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from pymdownx import superfences

from mdcheck.rules import lint_with_rules
from mdcheck.ollama_client import lint_with_llm


class EditorPane(QPlainTextEdit):
    """Markdown編集用のテキストエディタ"""
    
    textChangedDelayed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Monospace", 10))
        self.setTabStopDistance(40)
        
        # デバウンスタイマー（500ms）
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.textChangedDelayed.emit)
        
        self.textChanged.connect(self._on_text_changed)
    
    def _on_text_changed(self):
        """テキスト変更時にデバウンスタイマーを再起動"""
        self.debounce_timer.stop()
        self.debounce_timer.start(500)
    
    def highlight_line(self, line_number: int):
        """指定行をハイライト表示して移動"""
        cursor = QTextCursor(self.document().findBlockByLineNumber(line_number - 1))
        self.setTextCursor(cursor)
        self.centerCursor()


class PreviewPane(QWebEngineView):
    """Markdownプレビュー用のWebビュー"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHtml(self._get_empty_html())
    
    def update_preview(self, markdown_text: str):
        """Markdownテキストをレンダリング"""
        html_content = self._markdown_to_html(markdown_text)
        full_html = self._wrap_html(html_content)
        self.setHtml(full_html)
    
    def _markdown_to_html(self, text: str) -> str:
        """MarkdownをHTMLに変換（Mermaid対応）"""
        md = markdown.Markdown(
            extensions=[
                'fenced_code',
                'tables',
                'codehilite',
                'pymdownx.superfences',
            ],
            extension_configs={
                'pymdownx.superfences': {
                    'custom_fences': [
                        {
                            'name': 'mermaid',
                            'class': 'mermaid',
                            'format': self._mermaid_formatter
                        }
                    ]
                }
            }
        )
        return md.convert(text)
    
    def _mermaid_formatter(self, source, language, css_class, options, md, **kwargs):
        """Mermaidブロック用のカスタムフォーマッター"""
        return f'<div class="mermaid">\n{source}\n</div>'
    
    def _wrap_html(self, content: str) -> str:
        """HTMLテンプレートでラップ"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}
        h1 {{ font-size: 2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
        h3 {{ font-size: 1.25em; }}
        code {{
            background: #f6f8fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            line-height: 1.45;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}
        table th, table td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        table th {{
            background: #f6f8fa;
            font-weight: 600;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            padding-left: 16px;
            margin-left: 0;
            color: #666;
        }}
        a {{
            color: #0969da;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .mermaid {{
            text-align: center;
            margin: 20px 0;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</head>
<body>
    {content}
</body>
</html>
"""
    
    def _get_empty_html(self) -> str:
        """初期表示用の空HTML"""
        return self._wrap_html("<p style='color: #999; text-align: center;'>プレビューがここに表示されます</p>")


class IssuesPane(QListWidget):
    """問題リスト表示用のパネル"""
    
    lineJumpRequested = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemClicked.connect(self._on_item_clicked)
    
    def add_issue(self, issue_text: str, line_number: int | None = None, issue_type: str = "rule"):
        """問題を追加"""
        item = QListWidgetItem(issue_text)
        
        # 行番号を保存
        if line_number is not None:
            item.setData(Qt.ItemDataRole.UserRole, line_number)
        
        # タイプ別のアイコン/色（読みやすいライトなカラー）
        if issue_type == "ai":
            item.setForeground(QColor("#4A90E2"))  # ライトブルー
        else:
            item.setForeground(QColor("#E85D75"))  # ライトレッド
        
        self.addItem(item)
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """アイテムクリック時に該当行へジャンプ"""
        line_number = item.data(Qt.ItemDataRole.UserRole)
        if line_number is not None:
            self.lineJumpRequested.emit(line_number)
    
    def clear_issues(self):
        """問題リストをクリア"""
        self.clear()


class MDCheckGUI(QMainWindow):
    """メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.current_file: Path | None = None
        self.setup_ui()
        self.create_menus()
        self.setWindowTitle("MDCheck - Markdown Checker with Preview")
        self.resize(1400, 800)
    
    def setup_ui(self):
        """UIレイアウトのセットアップ"""
        central = QWidget()
        self.setCentralWidget(central)
        
        # メインの水平スプリッター（3分割）
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # エディタペイン
        self.editor = EditorPane()
        self.editor.textChangedDelayed.connect(self._on_editor_changed)
        splitter.addWidget(self.editor)
        
        # プレビューペイン
        self.preview = PreviewPane()
        splitter.addWidget(self.preview)
        
        # 問題パネル
        self.issues = IssuesPane()
        self.issues.lineJumpRequested.connect(self.editor.highlight_line)
        splitter.addWidget(self.issues)
        
        # 分割比率を設定（40:40:20）
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 2)
        
        layout = QVBoxLayout(central)
        layout.addWidget(splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ステータスバー
        self.statusBar().showMessage("準備完了")
    
    def create_menus(self):
        """メニューバーの作成"""
        menubar = self.menuBar()
        
        # ファイルメニュー
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # チェックメニュー
        check_menu = menubar.addMenu("&Check")
        
        check_rules_action = QAction("Run &Rules Check", self)
        check_rules_action.setShortcut("F5")
        check_rules_action.triggered.connect(self.run_rules_check)
        check_menu.addAction(check_rules_action)
        
        check_ai_action = QAction("Run &AI Check", self)
        check_ai_action.setShortcut("F6")
        check_ai_action.triggered.connect(self.run_ai_check)
        check_menu.addAction(check_ai_action)
        
        check_all_action = QAction("Run &All Checks", self)
        check_all_action.setShortcut("F7")
        check_all_action.triggered.connect(self.run_all_checks)
        check_menu.addAction(check_all_action)
    
    def open_file(self):
        """ファイルを開く"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md);;All Files (*)"
        )
        
        if file_path:
            try:
                path = Path(file_path)
                text = path.read_text(encoding="utf-8")
                self.editor.setPlainText(text)
                self.current_file = path
                self.setWindowTitle(f"MDCheck - {path.name}")
                self.statusBar().showMessage(f"読み込み完了: {path.name}")
            except Exception as e:
                self.statusBar().showMessage(f"エラー: {e}")
    
    def save_file(self):
        """現在のファイルを保存"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """名前を付けて保存"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File",
            "",
            "Markdown Files (*.md);;All Files (*)"
        )
        
        if file_path:
            path = Path(file_path)
            self._save_to_file(path)
            self.current_file = path
            self.setWindowTitle(f"MDCheck - {path.name}")
    
    def _save_to_file(self, path: Path):
        """ファイルに保存"""
        try:
            text = self.editor.toPlainText()
            path.write_text(text, encoding="utf-8")
            self.statusBar().showMessage(f"保存完了: {path.name}")
        except Exception as e:
            self.statusBar().showMessage(f"保存エラー: {e}")
    
    def _on_editor_changed(self):
        """エディタ変更時にプレビューを更新"""
        text = self.editor.toPlainText()
        self.preview.update_preview(text)
    
    def run_rules_check(self):
        """ルールベースのチェックを実行"""
        self.issues.clear_issues()
        self.statusBar().showMessage("ルールチェック実行中...")
        
        text = self.editor.toPlainText()
        result = lint_with_rules(text)
        
        rule_issues = result.get("rule_based_issues", [])
        
        if rule_issues:
            for issue_text in rule_issues:
                # 行番号を抽出（"行 X:" の形式を想定）
                line_number = self._extract_line_number(issue_text)
                self.issues.add_issue(issue_text, line_number, "rule")
            
            self.statusBar().showMessage(f"ルールチェック完了: {len(rule_issues)}件の問題")
        else:
            self.issues.add_issue("✓ 問題は見つかりませんでした", None, "rule")
            self.statusBar().showMessage("ルールチェック完了: 問題なし")
    
    def run_ai_check(self):
        """AIチェックを実行"""
        self.statusBar().showMessage("AIチェック実行中（時間がかかる場合があります）...")
        QApplication.processEvents()  # UIを更新
        
        text = self.editor.toPlainText()
        
        try:
            # 長いテキストは先頭1500文字に制限
            result = lint_with_llm(text[:1500])
            
            # 用語・固有名詞
            terms = result.get("terms", [])
            for t in terms:
                surface = t.get("surface", "???")
                note = t.get("note", "")
                self.issues.add_issue(f"[用語] {surface}: {note}", None, "ai")
            
            # 表記揺れ
            inconsistencies = result.get("inconsistencies", [])
            for i in inconsistencies:
                a = i.get("a", "?")
                b = i.get("b", "?")
                note = i.get("note", "")
                self.issues.add_issue(f"[表記揺れ] {a} <-> {b}: {note}", None, "ai")
            
            # 提案
            suggestions = result.get("suggestions", [])
            for s in suggestions:
                self.issues.add_issue(f"[提案] {s}", None, "ai")
            
            total = len(terms) + len(inconsistencies) + len(suggestions)
            self.statusBar().showMessage(f"AIチェック完了: {total}件の指摘")
            
        except Exception as e:
            self.issues.add_issue(f"❌ AIチェックエラー: {e}", None, "ai")
            self.statusBar().showMessage(f"AIチェックエラー: {e}")
    
    def run_all_checks(self):
        """すべてのチェックを実行"""
        self.issues.clear_issues()
        self.run_rules_check()
        self.run_ai_check()
    
    def _extract_line_number(self, issue_text: str) -> int | None:
        """問題テキストから行番号を抽出"""
        import re
        match = re.match(r"行\s*(\d+):", issue_text)
        if match:
            return int(match.group(1))
        return None


def main():
    """GUIアプリケーションのエントリーポイント"""
    app = QApplication(sys.argv)
    app.setApplicationName("MDCheck")
    
    window = MDCheckGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
