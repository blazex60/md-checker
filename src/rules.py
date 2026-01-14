import re

def check_header_spacing(lines: list[str]) -> list[str]:
    """見出し(#)の後にスペースがあるかチェック"""
    issues = []
    for i, line in enumerate(lines, 1):
        # 修正箇所: [^ \n] -> [^\s]
        # \s は半角スペース、全角スペース、タブ、改行などをすべて「空白」として扱います
        # 「#の塊」の直後に「空白以外」が来ている場合のみエラーとみなします
        if re.match(r"^#+[^\s]", line):
            issues.append(f"Line {i}: Header missing space (e.g. '# Title') -> {line.strip()}")
    return issues

def check_trailing_whitespace(lines: list[str]) -> list[str]:
    """行末の不要な空白をチェック"""
    issues = []
    for i, line in enumerate(lines, 1):
        # 行末が「空白+改行」または「タブ+改行」で終わっているか
        # ※Markdownの「2スペース改行」を許容したい場合は、ここを調整する必要があります
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
    """
    ルールベースの静的解析を実行する
    """
    lines = text.splitlines(keepends=True)
    
    suggestions = []
    suggestions.extend(check_header_spacing(lines))
    suggestions.extend(check_trailing_whitespace(lines))
    suggestions.extend(check_todos(lines))

    return {
        "rule_based_issues": suggestions
    }