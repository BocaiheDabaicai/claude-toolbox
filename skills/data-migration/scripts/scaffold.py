#!/usr/bin/env python3
"""生成数据迁移工作区。

用法：
  python scripts/scaffold.py <target-dir> [--name my-migration] [--title "客户数据迁移"] [--force]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_ROOT / "assets" / "template"
DOCS_TEMPLATE_DIR = SKILL_ROOT / "assets" / "docs-templates"
KIT_DIR = SKILL_ROOT / "assets" / "kit"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TEXT_SUFFIXES = {".py", ".toml", ".csv", ".md", ".txt", ".json", ".yaml", ".yml"}


def fail(message: str) -> None:
    print(f"\n[scaffold] {message}\n", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成数据迁移工作区")
    parser.add_argument("target", help="目标目录")
    parser.add_argument("--name", default="", help="项目 slug，默认取目标目录名")
    parser.add_argument("--title", default="", help="项目显示名称")
    parser.add_argument("--force", action="store_true", help="目标目录非空时仍然写入")
    return parser.parse_args()


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "data-migration"


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

    if not TEMPLATE_DIR.is_dir():
        fail(f"找不到模板目录：{TEMPLATE_DIR}")
    if not DOCS_TEMPLATE_DIR.is_dir():
        fail(f"找不到文档模板目录：{DOCS_TEMPLATE_DIR}")
    if target.exists() and any(target.iterdir()) and not args.force:
        fail(f"目标目录非空：{target}\n如需覆盖，追加 --force（不会删除已有文件）。")

    project_name = slugify(args.name or target.name)
    if not SLUG_RE.match(project_name):
        fail(f"项目 slug 不合法：{project_name}")
    project_title = args.title or args.name or project_name

    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE_DIR, target, dirs_exist_ok=True)

    docs_dir = target / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    for path in DOCS_TEMPLATE_DIR.iterdir():
        if path.is_file():
            shutil.copy2(path, docs_dir / path.name)

    walk_replace(
        target,
        {
            "__PROJECT_NAME__": project_name,
            "__PROJECT_TITLE__": project_title,
        },
    )

    print(
        f"""
[scaffold] 已生成：{target}
  项目名：{project_name}
  标题：{project_title}

下一步：
  cd {target}
  uv tool install "{KIT_DIR}"
  # 需要 MySQL / Excel 源时：uv tool install "{KIT_DIR}[all]"

  export TARGET_DSN='postgresql://user:pass@host:5432/app_db'
  # PostgreSQL / MySQL 源再 export SOURCE_DSN

  migration-kit profile --config migration.toml --out docs/profile.md
  migration-kit plan --config migration.toml
  migration-kit run --config migration.toml            # dry-run
  migration-kit run --config migration.toml --apply    # 备份并确认后写入
  migration-kit reconcile --config migration.toml --out docs/reconcile.md

先填 docs/migration-plan.md，再按计划执行。
"""
    )


if __name__ == "__main__":
    main()
