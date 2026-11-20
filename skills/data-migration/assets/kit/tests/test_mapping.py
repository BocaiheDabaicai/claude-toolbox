import pytest

from migration_kit.mapping import MappingError, load_mapping, validate_mapping


def test_load_and_validate_mapping(workspace):
    mapping = load_mapping(workspace / "mapping.csv")
    issues = validate_mapping(
        mapping,
        ["id", "name", "phone", "email", "company", "status"],
        ("legacy_id",),
        {"trim", "digits", "lower"},
    )

    assert len(mapping) == 6
    assert issues == []


def test_mapping_duplicate_target(tmp_path):
    path = tmp_path / "mapping.csv"
    path.write_text(
        "target_column,source_column,target_type\n"
        "name,name,text\n"
        "name,other,text\n",
        encoding="utf-8",
    )

    with pytest.raises(MappingError, match="重复"):
        load_mapping(path)


def test_validate_missing_source_and_key(workspace):
    mapping = load_mapping(workspace / "mapping.csv")
    issues = validate_mapping(
        mapping,
        ["id", "name"],
        ("missing_key",),
        {"trim", "digits", "lower"},
    )

    assert any("源列" in issue for issue in issues)
    assert any("run.key" in issue for issue in issues)


def test_validate_without_key_warns(workspace):
    mapping = load_mapping(workspace / "mapping.csv")
    issues = validate_mapping(
        mapping,
        ["id", "name", "phone", "email", "company", "status"],
        (),
        {"trim", "digits", "lower"},
    )

    assert any(issue.startswith("警告:") for issue in issues)
