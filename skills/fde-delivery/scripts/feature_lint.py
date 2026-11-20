#!/usr/bin/env python3
"""校验 docs/features.csv 的字段、状态和依赖。

用法：
  python feature_lint.py docs/features.csv [--strict]
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REQUIRED_COLUMNS = [
    "id",
    "module",
    "feature",
    "description",
    "priority",
    "status",
    "owner",
    "acceptance",
    "dependencies",
    "notes",
    "updated",
]
ALLOWED_STATUS = {
    "idea",
    "scoped",
    "in-progress",
    "blocked",
    "demo",
    "accepted",
    "deferred",
    "cut",
}
ALLOWED_PRIORITY = {"P0", "P1", "P2"}
OWNER_REQUIRED_STATUS = {"in-progress", "blocked", "demo", "accepted"}
ACCEPTANCE_REQUIRED_STATUS = {"accepted"}
ID_RE = re.compile(r"^F-\d{3,}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class Issue:
    level: str
    line: int
    message: str


def parse_dependencies(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[;,]", value)
    return [part.strip() for part in parts if part.strip()]


def lint_rows(rows: list[dict[str, str]]) -> list[Issue]:
    issues: list[Issue] = []
    ids: dict[str, int] = {}
    names: dict[str, int] = {}

    for line, row in enumerate(rows, start=2):
        item_id = (row.get("id") or "").strip()
        module = (row.get("module") or "").strip()
        feature = (row.get("feature") or "").strip()
        description = (row.get("description") or "").strip()
        priority = (row.get("priority") or "").strip()
        status = (row.get("status") or "").strip()
        owner = (row.get("owner") or "").strip()
        acceptance = (row.get("acceptance") or "").strip()
        notes = (row.get("notes") or "").strip()
        updated = (row.get("updated") or "").strip()

        if not ID_RE.match(item_id):
            issues.append(Issue("error", line, f"{item_id or '(空)'}: ID 必须是 F-001 形式"))
        elif item_id in ids:
            issues.append(
                Issue(
                    "error",
                    line,
                    f"{item_id}: ID 与第 {ids[item_id]} 行重复",
                )
            )
        else:
            ids[item_id] = line

        if not module:
            issues.append(Issue("error", line, f"{item_id}: module 不能为空"))
        if not feature:
            issues.append(Issue("error", line, f"{item_id}: feature 不能为空"))
        elif feature in names:
            issues.append(
                Issue(
                    "warning",
                    line,
                    f"{item_id}: feature 名称与第 {names[feature]} 行重复",
                )
            )
        else:
            names[feature] = line
        if not description:
            issues.append(Issue("error", line, f"{item_id}: description 不能为空"))

        if priority not in ALLOWED_PRIORITY:
            issues.append(
                Issue("error", line, f"{item_id}: priority 只允许 P0/P1/P2")
            )
        if status not in ALLOWED_STATUS:
            issues.append(
                Issue(
                    "error",
                    line,
                    f"{item_id}: status 不合法: {status or '(空)'}",
                )
            )

        if status in OWNER_REQUIRED_STATUS and not owner:
            issues.append(
                Issue("error", line, f"{item_id}: {status} 状态必须有 owner")
            )
        if status in ACCEPTANCE_REQUIRED_STATUS and not acceptance:
            issues.append(
                Issue("error", line, f"{item_id}: accepted 状态必须有 acceptance")
            )
        if status in {"scoped", "in-progress", "demo"} and not acceptance:
            issues.append(
                Issue("warning", line, f"{item_id}: 建议补充 acceptance")
            )
        if status in {"deferred", "cut"} and not notes:
            issues.append(
                Issue("warning", line, f"{item_id}: 暂缓/砍掉请在 notes 写原因")
            )
        if priority == "P0" and status == "idea":
            issues.append(
                Issue("warning", line, f"{item_id}: P0 还停留在 idea，尽快确认范围")
            )

        if not DATE_RE.match(updated):
            issues.append(
                Issue("error", line, f"{item_id}: updated 必须是 YYYY-MM-DD")
            )

        for dependency in parse_dependencies(row.get("dependencies") or ""):
            if dependency == item_id:
                issues.append(
                    Issue("error", line, f"{item_id}: 不能依赖自己")
                )
            elif dependency not in ids:
                # 依赖可能在后面的行，先记录，最后统一检查
                pass

    known_ids = set(ids)
    for line, row in enumerate(rows, start=2):
        item_id = (row.get("id") or "").strip()
        for dependency in parse_dependencies(row.get("dependencies") or ""):
            if dependency != item_id and dependency not in known_ids:
                issues.append(
                    Issue(
                        "error",
                        line,
                        f"{item_id}: 依赖不存在: {dependency}",
                    )
                )

    return issues


def summarize(rows: list[dict[str, str]]) -> str:
    status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    for row in rows:
        status = (row.get("status") or "").strip() or "(空)"
        priority = (row.get("priority") or "").strip() or "(空)"
        status_counts[status] = status_counts.get(status, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    def render(counts: dict[str, int]) -> str:
        return ", ".join(
            f"{key}={value}" for key, value in sorted(counts.items())
        )

    return (
        f"features: {len(rows)}\n"
        f"by status: {render(status_counts)}\n"
        f"by priority: {render(priority_counts)}"
    )


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        missing = [column for column in REQUIRED_COLUMNS if column not in headers]
        if missing:
            raise ValueError(f"缺少列: {', '.join(missing)}")
        return list(reader)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError, OSError):
                pass

    parser = argparse.ArgumentParser(description="校验 features.csv")
    parser.add_argument("path", help="docs/features.csv")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="把 warning 也视为失败",
    )
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.is_file():
        print(f"错误: 文件不存在: {path}", file=sys.stderr)
        return 1

    try:
        rows = load_rows(path)
    except (OSError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    issues = lint_rows(rows)
    print(summarize(rows))
    for issue in sorted(issues, key=lambda item: (item.line, item.level)):
        print(f"[{issue.level.upper()}] line {issue.line}: {issue.message}")

    errors = [issue for issue in issues if issue.level == "error"]
    warnings = [issue for issue in issues if issue.level == "warning"]
    print(f"errors: {len(errors)}, warnings: {len(warnings)}")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
