from __future__ import annotations

from opsctl.discovery import discover


def test_discovers_projects_and_skips_excluded(tmp_path, write_manifest, basic_manifest):
    write_manifest(tmp_path / "crm", basic_manifest)
    write_manifest(
        tmp_path / "shop",
        basic_manifest.replace('slug = "crm"', 'slug = "shop"').replace('"CRM"', '"Shop"'),
    )
    write_manifest(tmp_path / "node_modules" / "nested", basic_manifest)
    write_manifest(tmp_path / ".hidden" / "nested", basic_manifest)

    result = discover(tmp_path)

    assert [project.slug for project in result.projects] == ["crm", "shop"]
    assert result.errors == []


def test_discovers_root_project(tmp_path, write_manifest, basic_manifest):
    write_manifest(tmp_path, basic_manifest)

    result = discover(tmp_path)

    assert [project.slug for project in result.projects] == ["crm"]
    assert result.errors == []


def test_reports_invalid_manifest(tmp_path, write_manifest):
    write_manifest(tmp_path / "broken", "[project]\nslug = 'broken'\nname = 'Broken'\n")

    result = discover(tmp_path)

    assert result.projects == []
    assert len(result.errors) == 1
    assert "services" in result.errors[0][1]


def test_missing_root(tmp_path):
    result = discover(tmp_path / "missing")
    assert result.projects == []
    assert len(result.errors) == 1
