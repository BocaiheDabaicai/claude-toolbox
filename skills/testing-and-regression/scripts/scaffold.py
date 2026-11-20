#!/usr/bin/env python3
"""生成测试门禁与回归文档。

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
TEMPLATE_DIR = SKILL_ROOT / "assets" / "templates"
DOCS_TEMPLATE_DIR = SKILL_ROOT / "assets" / "docs-templates"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TEXT_SUFFIXES = {".md", ".toml", ".txt", ".json", ".yaml", ".yml", ".ts", ".py"}


def fail(message: str) -> None:
    print(f"\n[scaffold] {message}\n", file=sys.stderr)
    raise SystemExit(1)


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "project"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成测试门禁与回归文档")
    parser.add_argument("target", help="项目根目录")
    parser.add_argument("--name", default="", help="项目 slug")
    parser.add_argument("--title", default="", help="项目显示名称")
    parser.add_argument("--force", action="store_true", help="文件已存在时仍然写入")
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
    gate_path = target / "gate.toml"

    if not TEMPLATE_DIR.is_dir():
        fail(f"找不到模板目录：{TEMPLATE_DIR}")
    if gate_path.exists() and not args.force:
        fail(f"gate.toml 已存在：{gate_path}\n如需覆盖，追加 --force。")
    if docs.exists() and any(docs.iterdir()) and not args.force:
        fail(f"docs 目录非空：{docs}\n如需覆盖，追加 --force。")

    project_name = slugify(args.name or target.name)
    if not SLUG_RE.match(project_name):
        fail(f"项目 slug 不合法：{project_name}")
    project_title = args.title or args.name or project_name

    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE_DIR / "gate.toml", gate_path)

    docs.mkdir(parents=True, exist_ok=True)
    for path in DOCS_TEMPLATE_DIR.iterdir():
        if path.is_file():
            shutil.copy2(path, docs / path.name)

    walk_replace(
        target,
        {
            "__PROJECT_NAME__": project_name,
            "__PROJECT_TITLE__": project_title,
        },
    )

    gate_script = SKILL_ROOT / "scripts" / "gate.py"
    print(
        f"""
[scaffold] 已生成：
  {gate_path}
  {docs}

下一步：
  1. 修改 gate.toml 的 cwd / command / URL，匹配真实项目；
  2. 列出检查：
       python "{gate_script}" --config "{gate_path}" --list
  3. 预演：
       python "{gate_script}" --config "{gate_path}" --dry-run
  4. 执行门禁：
       python "{gate_script}" --config "{gate_path}"
  5. 前端/后端测试模板从 assets/templates 复制到对应项目。
"""
    )


if __name__ == "__main__":
    main()
