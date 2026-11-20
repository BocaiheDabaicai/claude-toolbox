"""opsctl 命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .discovery import DiscoveryResult, discover
from .doctor import format_checks, run_doctor
from .manifest import ProjectConfig
from .status import collect_status, format_status, to_dict
from .systemd import control, install_project, journal, render_project
from .util import Color, ManifestError, OpsError, color_enabled, print_json


def _configure_stdio() -> None:
    """Windows 控制台默认代码页可能不是 UTF-8，统一输出编码避免中文乱码。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def _add_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".", help="工作区根目录，默认当前目录")


def _load(args: argparse.Namespace) -> DiscoveryResult:
    root = Path(args.root).resolve()
    result = discover(root)
    for path, error in result.errors:
        print(f"警告: {path}: {error}", file=sys.stderr)
    if not result.projects:
        raise OpsError(f"在 {root} 下没有找到任何 ops/project.toml")
    return result


def _select(projects: list[ProjectConfig], slug: str | None) -> list[ProjectConfig]:
    if not slug:
        return projects
    matches = [project for project in projects if project.slug == slug]
    if not matches:
        available = ", ".join(project.slug for project in projects)
        raise OpsError(f"找不到项目 {slug}；可用项目: {available}")
    return matches


def cmd_list(args: argparse.Namespace) -> int:
    result = _load(args)
    if args.json:
        print_json(
            [
                {
                    "slug": project.slug,
                    "name": project.name,
                    "type": project.type,
                    "root": str(project.root),
                    "manifest": str(project.manifest_path),
                    "services": [
                        {
                            "name": service.name,
                            "unit": service.unit_name(project.slug),
                            "port": service.port,
                        }
                        for service in project.services
                    ],
                }
                for project in result.projects
            ]
        )
        return 0

    color = Color(color_enabled(args.no_color))
    for project in result.projects:
        print(f"{color.bold(project.name)} ({project.slug})  {color.dim(str(project.root))}")
        for service in project.services:
            port = f":{service.port}" if service.port is not None else ""
            print(f"  - {service.name}{port}  {color.dim(service.unit_name(project.slug))}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    result = _load(args)
    selected = _select(result.projects, args.project)
    statuses = [collect_status(project) for project in selected]

    healthy = all(status.state == "healthy" for status in statuses)
    if args.json:
        print_json([to_dict(status) for status in statuses])
        return 0 if healthy else 1

    color = Color(color_enabled(args.no_color))
    print("\n\n".join(format_status(status, color) for status in statuses))
    return 0 if healthy else 1


def cmd_control(args: argparse.Namespace) -> int:
    result = _load(args)
    selected = _select(result.projects, args.project)
    for project in selected:
        control(project, args.action, service=args.service, dry_run=args.dry_run)
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    result = _load(args)
    selected = _select(result.projects, args.project)
    for project in selected:
        written = install_project(project, apply=args.apply, dry_run=args.dry_run)
        mode = "已安装" if args.apply else "已生成"
        print(f"{project.slug}: {mode} {len(written)} 个单元")
        for path in written:
            print(f"  {path}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    result = _load(args)
    selected = _select(result.projects, args.project)
    for project in selected:
        for filename, content in render_project(project).items():
            print(f"# ===== {filename} =====")
            print(content, end="")
    return 0


def cmd_logs(args: argparse.Namespace) -> int:
    result = _load(args)
    selected = _select(result.projects, args.project)
    if len(selected) != 1:
        raise OpsError("logs 一次只能查看一个项目")
    journal(
        selected[0],
        service=args.service,
        follow=args.follow,
        lines=args.lines,
    )
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    result = discover(root)
    checks = run_doctor(result.projects, result.errors)
    color = Color(color_enabled(args.no_color))
    print(format_checks(checks, color))
    return 0 if all(check.status != "error" for check in checks) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="opsctl",
        description="单机多项目统一启动、停止、重启与状态管理",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--no-color", action="store_true", help="禁用彩色输出")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser("list", help="列出工作区内的项目")
    _add_root(p)
    p.add_argument("--json", action="store_true", help="输出 JSON")
    p.set_defaults(func=cmd_list)

    p = subparsers.add_parser("status", help="查看项目与服务的运行状态")
    _add_root(p)
    p.add_argument("project", nargs="?", help="项目 slug；不填则查看全部")
    p.add_argument("--json", action="store_true", help="输出 JSON")
    p.set_defaults(func=cmd_status)

    for action in ("start", "stop", "restart"):
        p = subparsers.add_parser(action, help=f"{action} 项目")
        _add_root(p)
        p.add_argument("project", nargs="?", help="项目 slug；不填则操作全部")
        p.add_argument("--service", help="只操作某个服务")
        p.add_argument("--dry-run", action="store_true", help="只打印命令")
        p.set_defaults(func=cmd_control, action=action)

    p = subparsers.add_parser("install", help="生成 systemd 单元；--apply 安装并启用")
    _add_root(p)
    p.add_argument("project", nargs="?", help="项目 slug；不填则处理全部")
    p.add_argument("--apply", action="store_true", help="复制到 /etc/systemd/system 并 enable")
    p.add_argument("--dry-run", action="store_true", help="只打印命令")
    p.set_defaults(func=cmd_install)

    p = subparsers.add_parser("render", help="打印 systemd 单元内容")
    _add_root(p)
    p.add_argument("project", nargs="?", help="项目 slug；不填则输出全部")
    p.set_defaults(func=cmd_render)

    p = subparsers.add_parser("logs", help="查看 journal 日志")
    _add_root(p)
    p.add_argument("project", help="项目 slug")
    p.add_argument("--service", help="只看某个服务")
    p.add_argument("-f", "--follow", action="store_true", help="持续跟踪")
    p.add_argument("-n", "--lines", type=int, default=100, help="显示行数，默认 100")
    p.set_defaults(func=cmd_logs)

    p = subparsers.add_parser("doctor", help="检查运行环境与 manifest")
    _add_root(p)
    p.set_defaults(func=cmd_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OpsError, ManifestError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("已取消", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
