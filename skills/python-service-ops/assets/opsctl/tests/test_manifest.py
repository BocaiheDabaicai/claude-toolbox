from __future__ import annotations

import pytest

from opsctl.manifest import load_project
from opsctl.util import ManifestError


def test_load_minimal(tmp_path, write_manifest, basic_manifest):
    path = write_manifest(tmp_path / "crm", basic_manifest)
    project = load_project(path)

    assert project.slug == "crm"
    assert project.name == "CRM"
    assert project.project_dir == (tmp_path / "crm").resolve()
    assert project.root == (tmp_path / "crm").resolve()
    assert project.target_name == "crm.target"
    assert len(project.services) == 1

    service = project.services[0]
    assert service.name == "web"
    assert service.unit_name(project.slug) == "crm-web.service"
    assert service.health_url(project) == "http://127.0.0.1:3000/healthz"
    assert service.restart == "on-failure"


def test_load_custom_fields(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"
        type = "nuxt"
        root = "app"
        env_file = ".env.production"
        user = "deploy"
        group = "deploy"
        after = ["postgresql.service"]

        [project.health]
        path = "/ready"
        timeout = 5

        [[services]]
        name = "web"
        kind = "node"
        command = "node server.js"
        port = 3000
        health = "http://127.0.0.1:3000/custom"
        environment = { NODE_ENV = "production", DEBUG = false }
        """,
    )
    project = load_project(path)
    service = project.services[0]

    assert project.type == "nuxt"
    assert project.root == (tmp_path / "crm" / "app").resolve()
    assert project.env_file == (tmp_path / "crm" / "app" / ".env.production").resolve()
    assert project.user == "deploy"
    assert project.after == ("postgresql.service",)
    assert project.health.path == "/ready"
    assert project.health.timeout == 5.0
    assert service.health_url(project) == "http://127.0.0.1:3000/custom"
    assert service.environment == {"NODE_ENV": "production", "DEBUG": "false"}


def test_health_url_derived_without_leading_slash(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"

        [project.health]
        path = "health"

        [[services]]
        name = "web"
        command = "node server.js"
        port = 3000
        """,
    )
    project = load_project(path)
    assert project.services[0].health_url(project) == "http://127.0.0.1:3000/health"


def test_rejects_bad_slug(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "../evil"
        name = "Evil"

        [[services]]
        name = "web"
        command = "true"
        """,
    )
    with pytest.raises(ManifestError):
        load_project(path)


def test_rejects_duplicate_service(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"

        [[services]]
        name = "web"
        command = "true"

        [[services]]
        name = "web"
        command = "true"
        """,
    )
    with pytest.raises(ManifestError, match="服务名重复"):
        load_project(path)


def test_rejects_unknown_before(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"

        [[services]]
        name = "web"
        command = "true"
        before = ["missing"]
        """,
    )
    with pytest.raises(ManifestError, match="before"):
        load_project(path)


def test_oneshot_forces_restart_no(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"

        [[services]]
        name = "migrate"
        command = "python migrate.py"
        oneshot = true
        restart = "always"
        """,
    )
    project = load_project(path)
    assert project.services[0].oneshot is True
    assert project.services[0].restart == "no"


def test_rejects_missing_services(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"
        """,
    )
    with pytest.raises(ManifestError, match="services"):
        load_project(path)


def test_rejects_invalid_systemd_name(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"

        [[services]]
        name = "web"
        command = "true"
        systemd = "crm-web"
        """,
    )
    with pytest.raises(ManifestError, match=".service"):
        load_project(path)


def test_rejects_systemd_name_with_path(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"

        [[services]]
        name = "web"
        command = "true"
        systemd = "../evil.service"
        """,
    )
    with pytest.raises(ManifestError, match="路径"):
        load_project(path)


def test_rejects_invalid_port(tmp_path, write_manifest):
    path = write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"

        [[services]]
        name = "web"
        command = "true"
        port = 70000
        """,
    )
    with pytest.raises(ManifestError, match="65535"):
        load_project(path)
