from __future__ import annotations

from opsctl.manifest import load_project
from opsctl.systemd import (
    control,
    install_project,
    render_project,
    render_service_unit,
    render_target_unit,
    write_units,
)


def _project(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"
        user = "deploy"
        group = "deploy"
        env_file = ".env.production"
        after = ["postgresql.service"]

        [[services]]
        name = "migrate"
        kind = "python"
        command = "python migrate.py"
        oneshot = true
        before = ["web"]

        [[services]]
        name = "web"
        kind = "node"
        command = "node server.js"
        port = 3000
        environment = { NODE_ENV = "production" }
        """,
    )
    return load_project(path)


def test_render_service_unit(tmp_path, write_manifest):
    project = _project(tmp_path, write_manifest)
    web = project.service_by_name("web")
    assert web is not None

    content = render_service_unit(project, web)

    assert "Description=CRM - web" in content
    assert "PartOf=crm.target" in content
    assert "After=network-online.target postgresql.service crm-migrate.service" in content
    assert "Requires=crm-migrate.service" in content
    assert "WorkingDirectory=" in content
    assert "EnvironmentFile=-" in content
    assert "Environment=NODE_ENV=production" in content
    assert "ExecStart=/bin/sh -lc" in content
    assert "Restart=on-failure" in content
    assert "RestartSec=3" in content
    assert "SyslogIdentifier=crm-web" in content


def test_render_oneshot_unit(tmp_path, write_manifest):
    project = _project(tmp_path, write_manifest)
    migrate = project.service_by_name("migrate")
    assert migrate is not None

    content = render_service_unit(project, migrate)

    assert "Type=oneshot" in content
    assert "RemainAfterExit=yes" in content
    assert "Before=crm-web.service" in content
    assert "Restart=no" in content
    assert "RestartSec=" not in content


def test_execstart_escapes_percent_and_quotes_environment(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"

        [[services]]
        name = "web"
        command = "node app.js --format=%Y"
        environment = { GREETING = "hello world" }
        """,
    )
    project = load_project(path)
    service = project.services[0]

    content = render_service_unit(project, service)

    assert "--format=%%Y" in content
    assert 'Environment="GREETING=hello world"' in content


def test_render_target_unit(tmp_path, write_manifest):
    project = _project(tmp_path, write_manifest)

    content = render_target_unit(project)

    assert "Wants=network-online.target crm-migrate.service crm-web.service" in content
    assert "crm-migrate.service" in content
    assert "crm-web.service" in content
    assert "WantedBy=multi-user.target" in content


def test_render_project_and_write_units(tmp_path, write_manifest):
    project = _project(tmp_path, write_manifest)

    rendered = render_project(project)
    assert set(rendered) == {"crm-migrate.service", "crm-web.service", "crm.target"}

    written = write_units(project)
    assert len(written) == 3
    for path in written:
        assert path.is_file()
        assert path.parent == project.project_dir / "ops" / "systemd"


def test_install_without_apply_only_writes(tmp_path, write_manifest):
    project = _project(tmp_path, write_manifest)

    written = install_project(project)

    assert len(written) == 3
    assert all(path.is_file() for path in written)


def test_control_dry_run(tmp_path, write_manifest, capsys):
    project = _project(tmp_path, write_manifest)

    control(project, "start", dry_run=True)

    output = capsys.readouterr().out
    assert "+ systemctl start crm.target" in output


def test_control_service_dry_run(tmp_path, write_manifest, capsys):
    project = _project(tmp_path, write_manifest)

    control(project, "restart", service="web", dry_run=True)

    output = capsys.readouterr().out
    assert "+ systemctl restart crm-web.service" in output


def test_install_apply_dry_run(tmp_path, write_manifest, capsys):
    project = _project(tmp_path, write_manifest)

    written = install_project(project, apply=True, dry_run=True)

    output = capsys.readouterr().out
    assert len(written) == 3
    assert "+ install -m 0644" in output
    assert "+ systemctl daemon-reload" in output
    assert "+ systemctl enable crm.target" in output
