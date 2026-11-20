from __future__ import annotations

import json

from opsctl.cli import main


def test_cli_list_json(tmp_path, write_manifest, basic_manifest, capsys):
    write_manifest(tmp_path / "crm", basic_manifest)

    code = main(["--no-color", "list", "--root", str(tmp_path), "--json"])

    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["slug"] == "crm"
    assert data[0]["services"][0]["unit"] == "crm-web.service"


def test_cli_render(tmp_path, write_manifest, basic_manifest, capsys):
    write_manifest(tmp_path / "crm", basic_manifest)

    code = main(["--no-color", "render", "crm", "--root", str(tmp_path)])

    assert code == 0
    output = capsys.readouterr().out
    assert "# ===== crm-web.service =====" in output
    assert "# ===== crm.target =====" in output
    assert "ExecStart=/bin/sh -lc" in output


def test_cli_status_json(tmp_path, write_manifest, capsys):
    write_manifest(
        tmp_path / "crm",
        """
        [project]
        slug = "crm"
        name = "CRM"

        [[services]]
        name = "web"
        command = "node server.js"
        """,
    )

    code = main(["--no-color", "status", "crm", "--root", str(tmp_path), "--json"])

    # Linux 上单元不存在时 status 非 0；Windows 上 systemd 不可用，按最佳努力返回。
    assert code in (0, 1)
    data = json.loads(capsys.readouterr().out)
    assert data[0]["project"] == "crm"
    assert data[0]["services"][0]["name"] == "web"


def test_cli_unknown_project(tmp_path, write_manifest, basic_manifest, capsys):
    write_manifest(tmp_path / "crm", basic_manifest)

    code = main(["--no-color", "status", "missing", "--root", str(tmp_path)])

    assert code == 1
    assert "找不到项目 missing" in capsys.readouterr().err


def test_cli_empty_root(tmp_path, capsys):
    code = main(["--no-color", "list", "--root", str(tmp_path)])

    assert code == 1
    assert "没有找到" in capsys.readouterr().err


def test_cli_start_dry_run(tmp_path, write_manifest, basic_manifest, capsys):
    write_manifest(tmp_path / "crm", basic_manifest)

    code = main(["--no-color", "start", "crm", "--root", str(tmp_path), "--dry-run"])

    assert code == 0
    assert "+ systemctl start crm.target" in capsys.readouterr().out
