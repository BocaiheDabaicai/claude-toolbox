from __future__ import annotations

from opsctl.health import HealthResult
from opsctl.manifest import load_project
from opsctl.status import (
    ProjectStatus,
    ServiceStatus,
    SystemdState,
    collect_status,
    format_status,
    to_dict,
)
from opsctl.util import Color


def _project(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"

        [[services]]
        name = "web"
        command = "node server.js"
        port = 3000
        """,
    )
    return load_project(path)


def _service_status(project, *, active=True, health_ok=True):
    service = project.services[0]
    return ServiceStatus(
        service=service,
        systemd=SystemdState(
            available=True,
            load_state="loaded",
            active_state="active" if active else "inactive",
            sub_state="running" if active else "dead",
            main_pid=1234 if active else None,
            restarts=2,
        ),
        health=HealthResult(health_ok, "HTTP 200" if health_ok else "HTTP 500", 12),
        port_open=active,
    )


def test_state_healthy(tmp_path, write_manifest):
    project = _project(tmp_path, write_manifest)
    status = ProjectStatus(project=project, services=[_service_status(project)])
    assert status.state == "healthy"


def test_state_degraded_when_systemd_inactive_but_health_ok(tmp_path, write_manifest):
    project = _project(tmp_path, write_manifest)
    status = ProjectStatus(
        project=project,
        services=[_service_status(project, active=False, health_ok=True)],
    )
    # systemd 显示 inactive，但端口/健康检查仍然通过：说明有进程但不是 systemd 管理的
    assert status.state == "degraded"


def test_state_stopped(tmp_path, write_manifest):
    project = _project(tmp_path, write_manifest)
    status = ProjectStatus(
        project=project,
        services=[_service_status(project, active=False, health_ok=False)],
    )
    assert status.state == "stopped"


def test_to_dict(tmp_path, write_manifest):
    project = _project(tmp_path, write_manifest)
    status = ProjectStatus(project=project, services=[_service_status(project)])

    data = to_dict(status)

    assert data["project"] == "crm"
    assert data["state"] == "healthy"
    assert data["services"][0]["unit"] == "crm-web.service"
    assert data["services"][0]["systemd"]["active_state"] == "active"
    assert data["services"][0]["health"]["ok"] is True
    assert data["services"][0]["port"] == 3000


def test_format_status(tmp_path, write_manifest):
    project = _project(tmp_path, write_manifest)
    status = ProjectStatus(project=project, services=[_service_status(project)])

    text = format_status(status, Color(False))

    assert "CRM (crm)" in text
    assert "healthy" in text
    assert "web" in text
    assert "crm-web.service" not in text  # 表格只显示 service 名，不显示单元名
    assert "1234" in text


def test_collect_status_without_health_check(tmp_path, write_manifest):
    project = _project(tmp_path, write_manifest)

    status = collect_status(project, check_health=False)

    assert len(status.services) == 1
    assert status.services[0].health is None
    assert status.services[0].port_open in (True, False)
