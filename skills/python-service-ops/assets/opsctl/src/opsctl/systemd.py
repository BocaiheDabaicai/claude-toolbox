"""systemd 单元渲染、安装与控制。"""

from __future__ import annotations

import shlex
from pathlib import Path

from .manifest import ProjectConfig, ServiceConfig
from .util import OpsError, SystemdError, is_root, require_systemd, run, which

SYSTEMD_DIR = Path("/etc/systemd/system")
UNIT_OUTPUT_DIR = Path("ops") / "systemd"


def _quote_env(value: str) -> str:
    if any(char in value for char in " \t\"'\\"):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def render_service_unit(project: ProjectConfig, service: ServiceConfig) -> str:
    unit_map = project.unit_map()
    # 如果别的服务声明了 before 本服务，本服务必须等它成功：
    # Requires 保证前置失败时本服务不启动，After 保证顺序。
    required = [
        other.unit_name(project.slug)
        for other in project.services
        if service.name in other.before
    ]
    after = list(dict.fromkeys(["network-online.target", *project.after, *required]))
    lines = [
        "[Unit]",
        f"Description={project.name} - {service.name}",
        "Wants=network-online.target",
        f"After={' '.join(after)}",
        f"PartOf={project.target_name}",
    ]
    if required:
        lines.append("Requires=" + " ".join(required))
    if service.before:
        before_units = [unit_map[dependency] for dependency in service.before]
        lines.append("Before=" + " ".join(before_units))

    lines.append("")
    lines.append("[Service]")
    if service.oneshot:
        lines.extend(["Type=oneshot", "RemainAfterExit=yes"])
    else:
        lines.append("Type=simple")
    if project.user:
        lines.append(f"User={project.user}")
    if project.group:
        lines.append(f"Group={project.group}")
    lines.append(f"WorkingDirectory={shlex.quote(str(service.working_dir or project.root))}")
    if project.env_file:
        lines.append(f"EnvironmentFile=-{shlex.quote(str(project.env_file))}")
    for key, value in service.environment.items():
        lines.append(f"Environment={_quote_env(f'{key}={value}')}")
    # systemd 会展开 ExecStart 里的 % 说明符；这里转义为字面量 %。
    command = service.command.replace("%", "%%")
    lines.append(f"ExecStart=/bin/sh -lc {shlex.quote(f'exec {command}')}")
    if service.oneshot:
        lines.append("Restart=no")
    else:
        lines.append(f"Restart={service.restart}")
        lines.append(f"RestartSec={service.restart_sec}")
    lines.extend(
        [
            f"TimeoutStopSec={service.timeout_stop_sec}",
            "KillSignal=SIGTERM",
            "StandardOutput=journal",
            "StandardError=journal",
            f"SyslogIdentifier={project.slug}-{service.name}",
        ]
    )
    return "\n".join(lines) + "\n"


def render_target_unit(project: ProjectConfig) -> str:
    units = [service.unit_name(project.slug) for service in project.services]
    wants = " ".join(["network-online.target", *units])
    after = " ".join(dict.fromkeys(["network-online.target", *units]))
    lines = [
        "[Unit]",
        f"Description={project.name}",
        f"Wants={wants}",
        f"After={after}",
        "",
        "[Install]",
        "WantedBy=multi-user.target",
    ]
    return "\n".join(lines) + "\n"


def render_project(project: ProjectConfig) -> dict[str, str]:
    units = {
        service.unit_name(project.slug): render_service_unit(project, service)
        for service in project.services
    }
    units[project.target_name] = render_target_unit(project)
    return units


def write_units(project: ProjectConfig) -> list[Path]:
    out_dir = project.project_dir / UNIT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, content in render_project(project).items():
        path = out_dir / filename
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def _sudo_prefix() -> list[str]:
    if is_root():
        return []
    if which("sudo"):
        return ["sudo"]
    raise SystemdError("需要 root 权限，且找不到 sudo")


def _resolve_unit(project: ProjectConfig, service: str | None) -> str:
    if not service:
        return project.target_name
    match = project.service_by_name(service)
    if not match:
        raise OpsError(f"项目 {project.slug} 没有服务 {service}")
    return match.unit_name(project.slug)


def install_project(
    project: ProjectConfig,
    *,
    apply: bool = False,
    dry_run: bool = False,
) -> list[Path]:
    """生成单元到 <project>/ops/systemd；apply=True 时安装并启用。"""
    written = write_units(project)
    if not apply:
        return written

    if dry_run:
        for path in written:
            run(["install", "-m", "0644", str(path), str(SYSTEMD_DIR / path.name)], dry_run=True)
        run(["systemctl", "daemon-reload"], dry_run=True)
        run(["systemctl", "enable", project.target_name], dry_run=True)
        return written

    require_systemd()
    prefix = _sudo_prefix()
    for path in written:
        run([*prefix, "install", "-m", "0644", str(path), str(SYSTEMD_DIR / path.name)])
    run([*prefix, "systemctl", "daemon-reload"])
    run([*prefix, "systemctl", "enable", project.target_name])
    return written


def control(
    project: ProjectConfig,
    action: str,
    *,
    service: str | None = None,
    dry_run: bool = False,
) -> None:
    if action not in {"start", "stop", "restart"}:
        raise OpsError(f"不支持的操作: {action}")
    unit = _resolve_unit(project, service)
    if dry_run:
        run(["systemctl", action, unit], dry_run=True)
        return
    require_systemd()
    prefix = _sudo_prefix()
    run([*prefix, "systemctl", action, unit])


def journal(
    project: ProjectConfig,
    *,
    service: str | None = None,
    follow: bool = False,
    lines: int = 100,
) -> None:
    if not which("journalctl"):
        raise SystemdError("找不到 journalctl")

    if service:
        units = [_resolve_unit(project, service)]
    else:
        units = [item.unit_name(project.slug) for item in project.services] or [project.target_name]

    args = ["journalctl"]
    for unit in units:
        args.extend(["-u", unit])
    args.extend(["-n", str(lines), "--no-pager"])
    if follow:
        args.append("-f")
    run(args, capture=False, check=False)
