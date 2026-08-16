from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "task-routing-master.md"


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    required = [
        "README.md",
        "task-routing-master.md",
        "TESTING.md",
        "LICENSE",
        "docs/ai-setup.md",
        "examples/routing-examples.md",
    ]
    for relative in required:
        check((ROOT / relative).is_file(), f"missing: {relative}", failures)

    if not MASTER.is_file():
        print("FAIL: master file is missing")
        return 1

    master = MASTER.read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    testing = (ROOT / "TESTING.md").read_text(encoding="utf-8")

    check("バージョン: 1.3.0" in master, "master version must be 1.3.0", failures)
    check("v1.1" not in master + readme, "stale v1.1 reference", failures)
    check("```mermaid" in master, "decision flow is missing", failures)
    check("絵の具を買う" in master, "shopping example is missing", failures)
    check("病院" in master, "hospital example is missing", failures)
    check("イラストを完成" in master, "production deadline example is missing", failures)
    check("AIへの渡し方" in master, "AI setup section is missing", failures)
    check("テスト状況" in master, "test status section is missing", failures)
    check("Trello実操作：公開版では未実施" in master, "external test scope is unclear", failures)
    check("Google Calendar実操作：公開版では未実施" in master, "Calendar test scope is unclear", failures)
    check("Calendar再確認前" in testing, "safe migration test is missing", failures)
    check("当日の開始時点から期限超過にしない" in master, "same-day deadline rule is missing", failures)
    check("終了時刻が開始時刻以前" in master, "invalid end-time rule is missing", failures)
    check("移管未完了として報告" in master, "archive-failure rule is missing", failures)
    check("二重登録しない" in master, "no-duplication rule is missing", failures)
    check("再確認できた後だけ" in readme, "safe migration summary is missing", failures)
    check("Calendar登録成功 and 再確認成功" in master, "migration condition is inconsistent", failures)

    heading_numbers = [int(n) for n in re.findall(r"^## (\d+)\.", master, re.MULTILINE)]
    check(heading_numbers == list(range(1, 46)), "numbered headings must be 1..45", failures)
    check(not re.search(r'^# \d+\.', master, re.MULTILINE), "section heading level is inconsistent", failures)
    check(not re.search(r'```(?:text|python) id=', master), "nonstandard code-fence ids remain", failures)

    case_numbers = [int(n) for n in re.findall(r"^(\d+)\.", testing, re.MULTILINE)]
    check(case_numbers == list(range(1, 45)), "test cases must be numbered 1..44", failures)

    markdown_files = list(ROOT.rglob("*.md"))
    for path in markdown_files:
        content = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]+\]\((?!https?://)([^)#]+)", content):
            resolved = (path.parent / target).resolve()
            check(resolved.exists(), f"broken link in {path.relative_to(ROOT)}: {target}", failures)

    sensitive_patterns = [
        r"https://trello\.com/c/",
        r"AIza[0-9A-Za-z_-]{20,}",
        r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
    ]
    public_text = "\n".join(p.read_text(encoding="utf-8") for p in markdown_files)
    for pattern in sensitive_patterns:
        check(not re.search(pattern, public_text), f"sensitive pattern found: {pattern}", failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print(f"{len(failures)} failure(s)")
        return 1

    print("PASS: repository documentation checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
