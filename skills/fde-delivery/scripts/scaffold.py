#!/usr/bin/env python3
"""把 FDE 交付文档模板复制到项目 docs/。

用法：
  python scaffold.py <project-dir> [--name my-project] [--title "我的项目"] [--force]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_ROOT / "assets" / "docs-templates"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TEXT_SUFFIXES = {".md", ".csv", ".txt", ".json", ".yaml", ".yml"}


def fail(message: str) -> None:
    print(f"\n[scaffold] {message}\n", file=sys.stderr)
    raise SystemExit(1)


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "project"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 FDE 交付文档")
    parser.add_argument("target", help="项目根目录")
    parser.add_argument("--name", default="", help="项目 slug")
    parser.add_argument("--title", default="", help="项目显示名称")
    parser.add_argument("--force", action="store_true", help="docs 非空时仍然写入")
    return parser.parse_args()


def walk_replace(root: Path, replacements: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        next_text = raw
        for old, new in replacements.items():
            next_text = next_text.replace(old, new)
        if next_text != raw:
            path.write_text(next_text, encoding="utf-8")


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError, OSError):
                pass

    args = parse_args()
    target = Path(args.target).resolve()
    docs = target / "docs"

    if not TEMPLATE_DIR.is_dir():
        fail(f"找不到模板目录：{TEMPLATE_DIR}")
    if docs.exists() and any(docs.iterdir()) and not args.force:
        fail(f"docs 目录非空：{docs}\n如需覆盖，追加 --force（不会删除已有文件）。")

    project_name = slugify(args.name or target.name)
    if not SLUG_RE.match(project_name):
        fail(f"项目 slug 不合法：{project_name}")
    project_title = args.title or args.name or project_name

    docs.mkdir(parents=True, exist_ok=True)
    for path in TEMPLATE_DIR.iterdir():
        if path.is_file():
            shutil.copy2(path, docs / path.name)

    walk_replace(
        docs,
        {
            "__PROJECT_NAME__": project_name,
            "__PROJECT_TITLE__": project_title,
        },
    )

    lint_script = SKILL_ROOT / "scripts" / "feature_lint.py"
    print(
        f"""
[scaffold] 已生成：{docs}
  项目名：{project_name}
  标题：{project_title}

下一步：
  1. 填 docs/brief.md：背景、目标、范围、Non-goals、干系人、风险
  2. 填 docs/features.csv：功能点、优先级、状态、验收标准、依赖
  3. 校验功能点台账：
       python "{lint_script}" "{docs / 'features.csv'}"
  4. 在 docs/roadmap.md 排垂直切片，每次只做一个切片
  5. 每完成一次开发/演示，追加 docs/delivery-log.md
  6. 验收时更新 docs/acceptance.md，交接时填 docs/handoff.md
"""
    )


if __name__ == "__main__":
    main()
