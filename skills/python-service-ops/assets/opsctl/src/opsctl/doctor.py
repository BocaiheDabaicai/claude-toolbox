"""运行环境与 manifest 自检。"""

from __future__ import annotations

import stat
import sys
from dataclasses import dataclass
from pathlib import Path

from .manifest import ProjectConfig
from .util import Color, is_linux, is_root, which


@dataclass(frozen=True)
class Check:
    name: str
    status: str  # ok | warn | error
    detail: str
    hint: str = ""


def _check_python() -> Check:
    version = sys.version.split()[0]
    if sys.version_info >= (3, 11):
        return Check("Python", "ok", version)
    return Check("Python", "error", version, "需要 Python 3.11+")


def _check_platform() -> Check:
    if is_linux():
        return Check("平台", "ok", "Linux")
    return Check(
        "平台",
        "warn",
        sys.platform,
        "systemd 管理只在 Linux 生效；其他系统可做 list / render / doctor",
    )


def _check_systemd() -> Check:
    path = which("systemctl")
    if path:
        return Check("systemctl", "ok", path)
    return Check("systemctl", "warn", "未找到", "生产服务器需要 systemd")


def _check_journal() -> Check:
    path = which("journalctl")
    if path:
        return Check("journalctl", "ok", path)
    return Check("journalctl", "warn", "未找到", "opsctl logs 依赖 journalctl")


def _check_privileges() -> Check:
    if not is_linux():
        return Check("权限", "warn", "非 Linux，跳过", "systemd 权限检查只在 Linux 生效")
    if is_root():
        return Check("权限", "ok", "root")
    if which("sudo"):
        return Check("权限", "warn", "非 root，存在 sudo", "启停/安装可能需要密码；建议配置最小 sudoers")
    return Check("权限", "error", "非 root 且无 sudo", "无法管理系统级 systemd 单元")


def _check_project(project: ProjectConfig) -> list[Check]:
    checks: list[Check] = []

    if not project.root.is_dir():
        checks.append(Check(f"{project.slug}: root", "error", str(project.root), "项目根目录不存在"))

    if project.env_file:
        if not project.env_file.is_file():
            checks.append(
                Check(
                    f"{project.slug}: env_file",
                    "warn",
                    str(project.env_file),
                    "文件不存在；systemd 会忽略（EnvironmentFile=-）",
                )
            )
        else:
            mode = project.env_file.stat().st_mode
            if mode & (stat.S_IRWXG | stat.S_IRWXO):
                checks.append(
                    Check(
                        f"{project.slug}: env_file 权限",
                        "warn",
                        oct(mode & 0o777),
                        "建议 chmod 600，避免密钥被其他用户读取",
                    )
                )

    for service in project.services:
        workdir = Path(service.working_dir) if service.working_dir else project.root
        if not workdir.is_dir():
            checks.append(
                Check(
                    f"{project.slug}:{service.name} working_dir",
                    "error",
                    str(workdir),
                    "工作目录不存在",
                )
            )
        first = service.command.split()[0] if service.command.split() else ""
        if first.startswith(("/", "./", "../")):
            candidate = Path(first) if first.startswith("/") else workdir / first
            if not candidate.exists():
                checks.append(
                    Check(
                        f"{project.slug}:{service.name} command",
                        "error",
                        first,
                        "命令路径不存在",
                    )
                )
        elif first and not which(first):
            checks.append(
                Check(
                    f"{project.slug}:{service.name} command",
                    "warn",
                    first,
                    "命令不在当前 PATH；systemd 使用 /bin/sh -lc，需确保登录 shell 能找到它",
                )
            )

    return checks


def run_doctor(
    projects: list[ProjectConfig],
    discovery_errors: list[tuple[Path, str]],
) -> list[Check]:
    checks = [
        _check_python(),
        _check_platform(),
        _check_systemd(),
        _check_journal(),
        _check_privileges(),
    ]
    for path, error in discovery_errors:
        checks.append(Check(f"manifest {path}", "error", error))
    for project in projects:
        checks.extend(_check_project(project))
    return checks


def format_checks(checks: list[Check], color: Color) -> str:
    icons = {
        "ok": color.green("OK"),
        "warn": color.yellow("WARN"),
        "error": color.red("ERROR"),
    }
    lines: list[str] = []
    for check in checks:
        lines.append(f"[{icons.get(check.status, check.status)}] {check.name}: {check.detail}")
        if check.hint:
            lines.append(f"       {color.dim(check.hint)}")
    return "\n".join(lines)
