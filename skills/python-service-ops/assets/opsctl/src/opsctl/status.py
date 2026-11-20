"""采集并格式化项目运行状态。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from .health import HealthResult, check_http, check_port
from .manifest import ProjectConfig, ServiceConfig
from .util import Color, which, run


@dataclass(frozen=True)
class SystemdState:
    available: bool
    load_state: str = "unknown"
    active_state: str = "unknown"
    sub_state: str = ""
    main_pid: int | None = None
    started_at: str = ""
    restarts: int = 0

    @property
    def is_active(self) -> bool:
        return self.active_state == "active"


@dataclass
class ServiceStatus:
    service: ServiceConfig
    systemd: SystemdState
    health: HealthResult | None
    port_open: bool | None

    @property
    def ok(self) -> bool:
        if self.systemd.available and not self.systemd.is_active:
            return False
        if self.service.port is not None and self.port_open is False:
            return False
        if self.health is not None and not self.health.ok:
            return False
        return True


@dataclass
class ProjectStatus:
    project: ProjectConfig
    services: list[ServiceStatus] = field(default_factory=list)

    @property
    def state(self) -> str:
        if not self.services:
            return "empty"
        if all(service.ok for service in self.services):
            return "healthy"
        if any(
            service.systemd.is_active
            or (service.health is not None and service.health.ok)
            or service.port_open
            for service in self.services
        ):
            return "degraded"
        return "stopped"


def _systemd_show(unit: str) -> SystemdState:
    if not which("systemctl"):
        return SystemdState(available=False)
    try:
        proc = run(
            [
                "systemctl",
                "show",
                "-p",
                "LoadState",
                "-p",
                "ActiveState",
                "-p",
                "SubState",
                "-p",
                "MainPID",
                "-p",
                "ExecMainStartTimestamp",
                "-p",
                "NRestarts",
                unit,
            ],
            check=False,
        )
    except Exception:
        return SystemdState(available=False)

    data: dict[str, str] = {}
    for line in (proc.stdout or "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            data[key] = value

    main_pid = data.get("MainPID", "0")
    restarts = data.get("NRestarts", "0")
    return SystemdState(
        available=True,
        load_state=data.get("LoadState", "unknown"),
        active_state=data.get("ActiveState", "unknown"),
        sub_state=data.get("SubState", ""),
        main_pid=int(main_pid) if main_pid.isdigit() and int(main_pid) > 0 else None,
        started_at=data.get("ExecMainStartTimestamp", ""),
        restarts=int(restarts) if restarts.isdigit() else 0,
    )


def _collect_service(
    project: ProjectConfig,
    service: ServiceConfig,
    *,
    check_health: bool,
) -> ServiceStatus:
    systemd_state = _systemd_show(service.unit_name(project.slug))
    port_open = None
    if service.port is not None:
        port_open = check_port("127.0.0.1", service.port).ok

    health = None
    if check_health:
        url = service.health_url(project)
        # 端口已经关闭时不再等 HTTP 超时，status 在大量服务下也能快速返回。
        if url and (service.port is None or port_open):
            health = check_http(url, project.health.timeout)

    return ServiceStatus(
        service=service,
        systemd=systemd_state,
        health=health,
        port_open=port_open,
    )


def collect_status(project: ProjectConfig, *, check_health: bool = True) -> ProjectStatus:
    result = ProjectStatus(project=project)
    if not project.services:
        return result

    workers = min(8, len(project.services))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        statuses = list(
            executor.map(
                lambda service: _collect_service(project, service, check_health=check_health),
                project.services,
            )
        )
    result.services.extend(statuses)
    return result


def to_dict(status: ProjectStatus) -> dict:
    return {
        "project": status.project.slug,
        "name": status.project.name,
        "type": status.project.type,
        "root": str(status.project.root),
        "state": status.state,
        "services": [
            {
                "name": item.service.name,
                "unit": item.service.unit_name(status.project.slug),
                "kind": item.service.kind,
                "port": item.service.port,
                "port_open": item.port_open,
                "systemd": {
                    "available": item.systemd.available,
                    "load_state": item.systemd.load_state,
                    "active_state": item.systemd.active_state,
                    "sub_state": item.systemd.sub_state,
                    "pid": item.systemd.main_pid,
                    "started_at": item.systemd.started_at,
                    "restarts": item.systemd.restarts,
                },
                "health": None
                if item.health is None
                else {
                    "ok": item.health.ok,
                    "detail": item.health.detail,
                    "latency_ms": item.health.latency_ms,
                },
                "ok": item.ok,
            }
            for item in status.services
        ],
    }


def format_status(status: ProjectStatus, color: Color) -> str:
    state_renderer = {
        "healthy": color.green,
        "degraded": color.yellow,
        "stopped": color.dim,
        "empty": color.dim,
    }.get(status.state, color.red)

    lines = [
        f"{color.bold(status.project.name)} ({status.project.slug})  "
        f"{state_renderer(status.state)}",
        color.dim(
            f"  {'SERVICE':<14} {'SYSTEMD':<14} {'PID':>8} {'PORT':>6} "
            f"{'HEALTH':<24} {'RESTARTS':>9}"
        ),
    ]

    for item in status.services:
        if not item.systemd.available:
            systemd_text = "n/a"
        elif item.systemd.load_state == "not-found":
            systemd_text = "not-found"
        else:
            systemd_text = item.systemd.active_state
            if item.systemd.sub_state and item.systemd.sub_state != "dead":
                systemd_text = f"{systemd_text}/{item.systemd.sub_state}"

        pid = str(item.systemd.main_pid) if item.systemd.main_pid else "-"
        port = str(item.service.port) if item.service.port is not None else "-"
        if item.health is not None:
            health_text = ("OK " if item.health.ok else "FAIL ") + item.health.detail
        elif item.service.port is not None:
            health_text = "PORT OPEN" if item.port_open else "PORT CLOSED"
        else:
            health_text = "-"
        restarts = str(item.systemd.restarts) if item.systemd.available else "-"

        lines.append(
            f"  {item.service.name:<14} {systemd_text:<14} {pid:>8} {port:>6} "
            f"{health_text:<24} {restarts:>9}"
        )

    return "\n".join(lines)
