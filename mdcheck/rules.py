import re

def check_header_spacing(lines: list[str]) -> list[str]:
    """見出し(#)の後に適切な空白があるかチェック"""
    issues = []
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith('#'):
            match = re.match(r"^(#+)(.*)", stripped)
            if match:
                rest = match.group(2)
                if not rest:
                    continue
                
                first_char = rest[0]
                if not first_char.isspace():
                    char_code = hex(ord(first_char))
                    issues.append(f"行 {i}: 見出しの後に空白がありません (文字コード: {char_code}) -> {line.strip()}")
                    
    return issues

def check_trailing_whitespace(lines: list[str]) -> list[str]:
    """行末の不要な空白をチェック"""
    issues = []
    for i, line in enumerate(lines, 1):
        if line.endswith(" \n") or line.endswith("\t\n"):
            issues.append(f"行 {i}: 行末に余計な空白があります")
    return issues

def check_todos(lines: list[str]) -> list[str]:
    """残っているTODOコメントをチェック"""
    issues = []
    for i, line in enumerate(lines, 1):
        if "TODO" in line or "FIXME" in line:
            issues.append(f"行 {i}: TODO/FIXMEが見つかりました -> {line.strip()}")
    return issues

def lint_with_rules(text: str) -> dict:
    lines = text.splitlines(keepends=True)
    suggestions = []
    suggestions.extend(check_header_spacing(lines))
    suggestions.extend(check_trailing_whitespace(lines))
    suggestions.extend(check_todos(lines))

    return {
        "rule_based_issues": suggestions
    }