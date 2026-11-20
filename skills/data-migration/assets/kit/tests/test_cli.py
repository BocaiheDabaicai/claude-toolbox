from migration_kit.cli import main


def test_cli_plan(workspace, capsys):
    code = main(["plan", "--config", str(workspace / "migration.toml")])

    assert code == 0
    output = capsys.readouterr().out
    assert "target: public.customers" in output
    assert "legacy_id <- id" in output


def test_cli_run_dry_run(workspace, capsys):
    code = main(["run", "--config", str(workspace / "migration.toml")])

    assert code == 0
    output = capsys.readouterr().out
    assert "mode: DRY-RUN" in output
    assert "processed: 3" in output


def test_cli_profile(workspace, capsys):
    code = main(["profile", "--config", str(workspace / "migration.toml")])

    assert code == 0
    assert "# 源数据画像" in capsys.readouterr().out
