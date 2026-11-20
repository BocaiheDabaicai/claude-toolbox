from migration_kit.config import load_config
from migration_kit.profile import format_profile_markdown, profile_source
from migration_kit.sources import open_source


def test_profile_csv(workspace):
    config = load_config(workspace / "migration.toml")
    source = open_source(config.source)
    try:
        profile = profile_source(source, sample_limit=2)
    finally:
        source.close()

    assert profile["total_rows"] == 3
    assert profile["profiled_rows"] == 3
    assert profile["nulls"].get("phone", 0) == 0
    assert profile["empties"].get("phone", 0) == 1
    assert profile["nulls"].get("email", 0) == 0
    assert profile["empties"].get("email", 0) == 2
    assert len(profile["samples"]) == 2

    markdown = format_profile_markdown(profile)
    assert "# 源数据画像" in markdown
    assert "| 列 |" in markdown
