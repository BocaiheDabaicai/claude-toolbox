from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import load_config, redact_dsn
from .mapping import load_mapping, validate_mapping
from .profile import format_profile_markdown, profile_source
from .reconcile import format_reconcile_markdown, run_reconcile
from .runner import run_migration
from .sources import open_source
from .transforms import load_transforms


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def _load_bundle(config_path: str):
    config = load_config(config_path)
    mapping = load_mapping(config.mapping.file)
    transforms = load_transforms(config.mapping.transform_module, config.base_dir)
    source = open_source(config.source)
    return config, mapping, transforms, source


def _report_issues(issues: list[str]) -> bool:
    errors = [issue for issue in issues if not issue.startswith("警告:")]
    for issue in issues:
        prefix = "WARN" if issue.startswith("警告:") else "ERROR"
        print(f"[{prefix}] {issue}")
    return bool(errors)


def cmd_profile(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    source = open_source(config.source)
    try:
        profile = profile_source(
            source,
            sample_limit=args.sample_limit,
            limit=args.limit,
        )
    finally:
        source.close()

    markdown = format_profile_markdown(profile)
    if args.out:
        Path(args.out).write_text(markdown, encoding="utf-8")
        print(f"画像已写入 {args.out}")
    else:
        print(markdown)
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    config, mapping, transforms, source = _load_bundle(args.config)
    try:
        issues = validate_mapping(
            mapping,
            source.columns,
            config.run.key,
            set(transforms),
        )
    finally:
        source.close()

    print(f"source: {config.source.type}")
    print(f"target: {config.target.schema}.{config.target.table}")
    print(f"target dsn: {redact_dsn(config.target.dsn)}")
    print(f"key: {', '.join(config.run.key) or '(none)'}")
    print("columns:")
    for column in mapping:
        source_column = column.source_column or "(default)"
        transform = f" transform={column.transform}" if column.transform else ""
        required = " required" if column.required else ""
        print(
            f"  {column.target_column} <- {source_column}"
            f" ({column.target_type}{required}{transform})"
        )
    return 1 if _report_issues(issues) else 0


def cmd_run(args: argparse.Namespace) -> int:
    config, mapping, transforms, source = _load_bundle(args.config)
    try:
        issues = validate_mapping(
            mapping,
            source.columns,
            config.run.key,
            set(transforms),
        )
        if _report_issues(issues):
            return 1

        mode = "APPLY" if args.apply else "DRY-RUN"
        print(f"mode: {mode}")
        print(f"source: {config.source.type}")
        print(f"target: {redact_dsn(config.target.dsn)} / {config.target.table}")
        result = run_migration(
            config,
            source,
            mapping,
            transforms,
            apply=args.apply,
            limit=args.limit,
            reset_state=args.reset_state,
            batch_size=args.batch_size,
        )
    finally:
        source.close()

    print(f"processed: {result.processed}")
    print(f"{'written' if args.apply else 'would-write'}: {result.written}")
    print(f"skipped: {result.skipped}")
    print(f"state: {result.state}")
    if result.sample:
        print("sample:")
        for item in result.sample:
            print(f"  {item}")
    for error in result.errors:
        print(f"[ERROR] {error}", file=sys.stderr)
    return 1 if result.errors else 0


def cmd_reconcile(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    results = run_reconcile(config)
    markdown = format_reconcile_markdown(results)
    if args.out:
        Path(args.out).write_text(markdown, encoding="utf-8")
        print(f"对账结果已写入 {args.out}")
    else:
        print(markdown)
    return 0 if all(item.passed for item in results) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="migration-kit",
        description="PostgreSQL 数据迁移：画像、映射检查、dry-run、加载、对账",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("profile", help="生成源数据画像")
    p.add_argument("--config", required=True, help="migration.toml")
    p.add_argument("--out", help="输出 Markdown 文件")
    p.add_argument("--sample-limit", type=int, default=5)
    p.add_argument("--limit", type=int, help="最多分析多少行")
    p.set_defaults(func=cmd_profile)

    p = sub.add_parser("plan", help="校验映射，不写数据")
    p.add_argument("--config", required=True, help="migration.toml")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("run", help="执行迁移；默认 dry-run，--apply 才写入")
    p.add_argument("--config", required=True, help="migration.toml")
    p.add_argument("--apply", action="store_true", help="真正写入目标库")
    p.add_argument("--limit", type=int, help="最多处理多少行")
    p.add_argument("--batch-size", type=int, help="覆盖配置中的 batch_size")
    p.add_argument("--reset-state", action="store_true", help="忽略断点状态重新开始")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("reconcile", help="执行配置中的对账 SQL")
    p.add_argument("--config", required=True, help="migration.toml")
    p.add_argument("--out", help="输出 Markdown 文件")
    p.set_defaults(func=cmd_reconcile)

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("已取消", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
