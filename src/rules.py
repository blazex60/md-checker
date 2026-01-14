import re

def check_header_spacing(lines: list[str]) -> list[str]:
    """見出し(#)の後に適切な空白があるかチェック"""
    issues = []
    for i, line in enumerate(lines, 1):
        # 先頭の空白を除去してチェック
        stripped = line.lstrip()
        
        # #で始まる行のみ対象
        if stripped.startswith('#'):
            # #の連続部分を取得
            # 例: "## 1. Title" -> match.group(1)="##", match.group(2)=" 1. Title"
            match = re.match(r"^(#+)(.*)", stripped)
            if match:
                hashes = match.group(1)
                rest = match.group(2)
                
                # #しかない行（##\n など）はOKとする
                if not rest:
                    continue
                
                # #の直後の文字を取得
                first_char = rest[0]
                
                # 直後の文字が「空白文字」でなければエラー
                # isspace()は半角/全角スペース/NBSP/タブ/改行すべてTrueを返します
                if not first_char.isspace():
                    # デバッグ用に文字コードを表示（原因特定のため）
                    char_code = hex(ord(first_char))
                    issues.append(f"Line {i}: Header missing space (found char {char_code}) -> {line.strip()}")
                    
    return issues

def check_trailing_whitespace(lines: list[str]) -> list[str]:
    """行末の不要な空白をチェック"""
    issues = []
    for i, line in enumerate(lines, 1):
        # 行末が「空白+改行」または「タブ+改行」の場合
        if line.endswith(" \n") or line.endswith("\t\n"):
            issues.append(f"Line {i}: Trailing whitespace detected")
    return issues

def check_todos(lines: list[str]) -> list[str]:
    """残っているTODOコメントをチェック"""
    issues = []
    for i, line in enumerate(lines, 1):
        if "TODO" in line or "FIXME" in line:
            issues.append(f"Line {i}: Found TODO/FIXME -> {line.strip()}")
    return issues

def lint_with_rules(text: str) -> dict:
    """ルールベースの静的解析を実行する"""
    lines = text.splitlines(keepends=True)
    
    suggestions = []
    suggestions.extend(check_header_spacing(lines))
    suggestions.extend(check_trailing_whitespace(lines))
    suggestions.extend(check_todos(lines))

    return {
        "rule_based_issues": suggestions
    }