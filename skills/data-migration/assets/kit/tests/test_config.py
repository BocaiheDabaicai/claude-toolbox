import pytest

from migration_kit.config import ConfigError, load_config, redact_dsn


def test_load_config(workspace):
    config = load_config(workspace / "migration.toml")

    assert config.source.type == "csv"
    assert config.source.path == (workspace / "data" / "customers.csv")
    assert config.target.table == "customers"
    assert config.mapping.file == (workspace / "mapping.csv")
    assert config.run.key == ("legacy_id",)
    assert config.run.batch_size == 2
    assert config.run.state_file == (workspace / ".migration-state.json")


def test_redact_dsn():
    assert redact_dsn("postgresql://user:secret@host/db") == "postgresql://user:***@host/db"
    assert redact_dsn("") == ""


def test_missing_env(workspace, monkeypatch):
    monkeypatch.delenv("TARGET_DSN")

    with pytest.raises(ConfigError, match="TARGET_DSN"):
        load_config(workspace / "migration.toml")
