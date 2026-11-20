import pytest

from migration_kit.config import load_config
from migration_kit.mapping import load_mapping
from migration_kit.runner import MigrationError, run_migration
from migration_kit.sources import open_source
from migration_kit.transforms import load_transforms


def _bundle(workspace):
    config = load_config(workspace / "migration.toml")
    mapping = load_mapping(config.mapping.file)
    transforms = load_transforms(config.mapping.transform_module, config.base_dir)
    source = open_source(config.source)
    return config, mapping, transforms, source


def test_dry_run_transforms_rows(workspace):
    config, mapping, transforms, source = _bundle(workspace)
    try:
        result = run_migration(
            config,
            source,
            mapping,
            transforms,
            apply=False,
        )
    finally:
        source.close()

    assert result.processed == 3
    assert result.written == 3
    assert result.skipped == 0
    assert result.sample[0]["legacy_id"] == 1
    assert result.sample[0]["name"] == "张明"
    assert result.sample[1]["phone"] == "13800000002"
    assert not (workspace / ".migration-state.json").exists()


def test_limit(workspace):
    config, mapping, transforms, source = _bundle(workspace)
    try:
        result = run_migration(
            config,
            source,
            mapping,
            transforms,
            apply=False,
            limit=2,
        )
    finally:
        source.close()

    assert result.processed == 2
    assert result.written == 2


def test_required_error(workspace):
    config, mapping, transforms, source = _bundle(workspace)
    try:
        # 第一行 name 为空，required=true，on_error=stop
        source.iter_rows = lambda **_: iter(
            [
                (
                    0,
                    {
                        "id": "1",
                        "name": "",
                        "phone": "",
                        "email": "",
                        "company": "",
                        "status": "ACTIVE",
                    },
                )
            ]
        )
        with pytest.raises(MigrationError, match="必填列"):
            run_migration(config, source, mapping, transforms, apply=False)
    finally:
        source.close()


def test_on_error_skip(workspace):
    config, mapping, transforms, source = _bundle(workspace)
    config = config.__class__(
        source=config.source,
        target=config.target,
        mapping=config.mapping,
        run=config.run.__class__(
            batch_size=config.run.batch_size,
            key=config.run.key,
            state_file=config.run.state_file,
            sample_limit=config.run.sample_limit,
            on_error="skip",
        ),
        reconcile_checks=config.reconcile_checks,
        path=config.path,
        base_dir=config.base_dir,
    )
    try:
        source.iter_rows = lambda **_: iter(
            [
                (
                    0,
                    {
                        "id": "1",
                        "name": "",
                        "phone": "",
                        "email": "",
                        "company": "",
                        "status": "ACTIVE",
                    },
                ),
                (
                    1,
                    {
                        "id": "2",
                        "name": "李静",
                        "phone": "",
                        "email": "",
                        "company": "",
                        "status": "ACTIVE",
                    },
                ),
            ]
        )
        result = run_migration(config, source, mapping, transforms, apply=False)
    finally:
        source.close()

    assert result.processed == 2
    assert result.skipped == 1
    assert result.errors
