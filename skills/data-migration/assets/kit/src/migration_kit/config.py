from __future__ import annotations

import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ENV_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class SourceConfig:
    type: str
    path: Path | None = None
    dsn: str | None = None
    schema: str = "public"
    table: str | None = None
    cursor_column: str | None = None
    where: str | None = None
    encoding: str = "utf-8"
    delimiter: str = ","
    sheet: str | None = None


@dataclass(frozen=True)
class TargetConfig:
    dsn: str
    table: str
    schema: str = "public"


@dataclass(frozen=True)
class MappingConfig:
    file: Path
    transform_module: str = "transforms"


@dataclass(frozen=True)
class RunConfig:
    batch_size: int = 1000
    key: tuple[str, ...] = ()
    state_file: Path = Path(".migration-state.json")
    sample_limit: int = 5
    on_error: str = "stop"


@dataclass(frozen=True)
class ReconcileCheck:
    name: str
    source_sql: str
    target_sql: str
    tolerance: str = "0"


@dataclass(frozen=True)
class MigrationConfig:
    source: SourceConfig
    target: TargetConfig
    mapping: MappingConfig
    run: RunConfig
    reconcile_checks: tuple[ReconcileCheck, ...]
    path: Path
    base_dir: Path


def expand_env(value: Any) -> Any:
    if isinstance(value, str):

        def replace(match: re.Match[str]) -> str:
            name = match.group(1)
            if name not in os.environ:
                raise ConfigError(f"环境变量未设置: {name}")
            return os.environ[name]

        return ENV_RE.sub(replace, value)
    if isinstance(value, list):
        return [expand_env(item) for item in value]
    if isinstance(value, dict):
        return {key: expand_env(item) for key, item in value.items()}
    return value


def _as_str(data: dict[str, Any], key: str, *, required: bool = True) -> str | None:
    value = data.get(key)
    if value is None:
        if required:
            raise ConfigError(f"缺少配置: {key}")
        return None
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"配置必须是字符串: {key}")
    return value.strip()


def _as_int(data: dict[str, Any], key: str, default: int, *, minimum: int = 1) -> int:
    value = data.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ConfigError(f"配置必须是 >= {minimum} 的整数: {key}")
    return value


def _resolve(base: Path, value: str | None) -> Path | None:
    return (base / value).resolve() if value else None


def load_config(path: str | Path) -> MigrationConfig:
    config_path = Path(path).resolve()
    try:
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"配置文件不存在: {config_path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"TOML 解析失败: {exc}") from exc

    data = expand_env(raw)
    base = config_path.parent

    source_data = data.get("source")
    if not isinstance(source_data, dict):
        raise ConfigError("缺少 [source]")
    source_type = (_as_str(source_data, "type") or "").lower()
    if source_type not in {"csv", "postgres", "mysql", "excel"}:
        raise ConfigError("source.type 只允许 csv / postgres / mysql / excel")

    source_path = None
    source_dsn = None
    source_table = None
    if source_type in {"csv", "excel"}:
        source_path = _resolve(base, _as_str(source_data, "path"))
    else:
        source_dsn = _as_str(source_data, "dsn")
        source_table = _as_str(source_data, "table")

    source = SourceConfig(
        type=source_type,
        path=source_path,
        dsn=source_dsn,
        schema=_as_str(source_data, "schema", required=False) or "public",
        table=source_table,
        cursor_column=_as_str(source_data, "cursor_column", required=False),
        where=_as_str(source_data, "where", required=False),
        encoding=_as_str(source_data, "encoding", required=False) or "utf-8",
        delimiter=_as_str(source_data, "delimiter", required=False) or ",",
        sheet=_as_str(source_data, "sheet", required=False),
    )

    target_data = data.get("target")
    if not isinstance(target_data, dict):
        raise ConfigError("缺少 [target]")
    target = TargetConfig(
        dsn=_as_str(target_data, "dsn") or "",
        table=_as_str(target_data, "table") or "",
        schema=_as_str(target_data, "schema", required=False) or "public",
    )

    mapping_data = data.get("mapping")
    if not isinstance(mapping_data, dict):
        raise ConfigError("缺少 [mapping]")
    mapping_file = _resolve(base, _as_str(mapping_data, "file"))
    if mapping_file is None:
        raise ConfigError("缺少 mapping.file")
    mapping = MappingConfig(
        file=mapping_file,
        transform_module=_as_str(mapping_data, "transform_module", required=False)
        or "transforms",
    )

    run_data = data.get("run", {})
    if not isinstance(run_data, dict):
        raise ConfigError("[run] 必须是表")
    key_value = run_data.get("key", [])
    if not isinstance(key_value, list) or any(
        not isinstance(item, str) or not item.strip() for item in key_value
    ):
        raise ConfigError("run.key 必须是字符串数组")
    on_error = (_as_str(run_data, "on_error", required=False) or "stop").lower()
    if on_error not in {"stop", "skip"}:
        raise ConfigError("run.on_error 只允许 stop / skip")

    run = RunConfig(
        batch_size=_as_int(run_data, "batch_size", 1000),
        key=tuple(item.strip() for item in key_value),
        state_file=_resolve(
            base,
            _as_str(run_data, "state_file", required=False) or ".migration-state.json",
        )
        or (base / ".migration-state.json"),
        sample_limit=_as_int(run_data, "sample_limit", 5, minimum=0),
        on_error=on_error,
    )

    reconcile_data = data.get("reconcile", {})
    if not isinstance(reconcile_data, dict):
        raise ConfigError("[reconcile] 必须是表")
    checks_raw = reconcile_data.get("checks", [])
    if not isinstance(checks_raw, list):
        raise ConfigError("reconcile.checks 必须是数组")
    checks: list[ReconcileCheck] = []
    for index, item in enumerate(checks_raw):
        if not isinstance(item, dict):
            raise ConfigError(f"reconcile.checks[{index}] 必须是表")
        checks.append(
            ReconcileCheck(
                name=_as_str(item, "name") or f"check-{index + 1}",
                source_sql=_as_str(item, "source_sql") or "",
                target_sql=_as_str(item, "target_sql") or "",
                tolerance=str(item.get("tolerance", "0")),
            )
        )

    return MigrationConfig(
        source=source,
        target=target,
        mapping=mapping,
        run=run,
        reconcile_checks=tuple(checks),
        path=config_path,
        base_dir=base,
    )


def redact_dsn(dsn: str | None) -> str:
    if not dsn:
        return ""
    return re.sub(r"(://[^:/@]+:)[^@]+(@)", r"\1***\2", dsn)
