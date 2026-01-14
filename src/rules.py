import re

def check_header_spacing(lines: list[str]) -> list[str]:
    """見出し(#)の後にスペースがあるかチェック"""
    issues = []
    for i, line in enumerate(lines, 1):
        # #で始まり、直後にスペースがなく、かつ改行のみの行ではない場合
        if re.match(r"^#+[^ \n]", line):
            issues.append(f"Line {i}: Header missing space (e.g. '# Title') -> {line.strip()}")
    return issues

def check_trailing_whitespace(lines: list[str]) -> list[str]:
    """行末の不要な空白をチェック"""
    issues = []
    for i, line in enumerate(lines, 1):
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
    戻り値はLLMの解析結果とフォーマットを合わせる
    """
    lines = text.splitlines(keepends=True)
    
    # 指摘事項をリストにまとめる
    suggestions = []
    suggestions.extend(check_header_spacing(lines))
    suggestions.extend(check_trailing_whitespace(lines))
    suggestions.extend(check_todos(lines))

    return {
        "rule_based_issues": suggestions
    }