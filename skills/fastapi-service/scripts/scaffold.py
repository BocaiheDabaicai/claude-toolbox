#!/usr/bin/env python3
"""生成 FastAPI 服务项目。

用法：
  python scripts/scaffold.py <target-dir> [--name my-api] [--title "我的 API"] [--force]
"""

from __future__ import annotations

import argparse
import base64
import os
import re
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_ROOT / "assets" / "template"
DOCS_TEMPLATE_DIR = SKILL_ROOT / "assets" / "docs-templates"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TEXT_SUFFIXES = {
    ".py",
    ".toml",
    ".ini",
    ".mako",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".example",
}
SECRET_PLACEHOLDER = "replace-with-at-least-32-random-characters"


def fail(message: str) -> None:
    print(f"\n[scaffold] {message}\n", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 FastAPI 服务项目")
    parser.add_argument("target", help="目标目录")
    parser.add_argument("--name", default="", help="项目 slug，默认取目标目录名")
    parser.add_argument("--title", default="", help="项目显示名称")
    parser.add_argument("--force", action="store_true", help="目标目录非空时仍然写入")
    return parser.parse_args()


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "fastapi-service"


def is_text_file(path: Path) -> bool:
    return path.name.startswith(".env") or path.suffix.lower() in TEXT_SUFFIXES


def replace_in_file(path: Path, replacements: dict[str, str]) -> None:
    if not is_text_file(path):
        return
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    next_text = raw
    for old, new in replacements.items():
        next_text = next_text.replace(old, new)
    if next_text != raw:
        path.write_text(next_text, encoding="utf-8")


def walk_replace(root: Path, replacements: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if path.is_file():
            replace_in_file(path, replacements)


def create_env(target: Path) -> bool:
    example = target / ".env.example"
    env_path = target / ".env"
    if not example.is_file() or env_path.exists():
        return False

    secret = base64.urlsafe_b64encode(os.urandom(48)).decode().rstrip("=")
    content = example.read_text(encoding="utf-8").replace(SECRET_PLACEHOLDER, secret)
    env_path.write_text(content, encoding="utf-8")
    return True


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
            "__PROJECT_SLUG__": project_name,
            "__PROJECT_DB__": project_name.replace("-", "_"),
            "__PROJECT_TITLE__": project_title,
        },
    )

    env_created = create_env(target)

    print(
        f"""
[scaffold] 已生成：{target}
  项目名：{project_name}
  标题：{project_title}
  {"已生成 .env，并随机生成 JWT_SECRET" if env_created else ".env 已存在，未覆盖"}

下一步：
  cd {target}
  # 修改 .env：DATABASE_URL、SEED_ADMIN_EMAIL、SEED_ADMIN_PASSWORD
  uv sync
  uv run alembic upgrade head
  uv run python -m scripts.seed
  uv run uvicorn app.main:app --reload --port 8000

接入顺序：
  1. 先填 docs/backend-contract.md、docs/data-model.md
  2. 在 app/db/models.py 加表，再 uv run alembic revision --autogenerate -m "add xxx"
  3. 在 app/modules/<domain>/ 下加 schemas / repository / service / router
  4. 在 app/api.py 挂载路由
  5. uv run pytest && uv run ruff check .
  6. 部署前确认 ops/project.toml 与端口、健康路径一致
"""
    )


if __name__ == "__main__":
    main()
