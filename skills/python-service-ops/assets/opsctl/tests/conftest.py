from __future__ import annotations

import textwrap
from pathlib import Path

import pytest


@pytest.fixture
def write_manifest():
    def _write(project_dir: Path, content: str) -> Path:
        path = project_dir / "ops" / "project.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
        return path

    return _write


@pytest.fixture
def basic_manifest():
    return """
    [project]
    slug = "crm"
    name = "CRM"

    [[services]]
    name = "web"
    command = "node server.js"
    port = 3000
    """
