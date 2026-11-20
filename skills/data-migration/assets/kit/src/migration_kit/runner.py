from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .config import MigrationConfig
from .mapping import MappingColumn
from .sources import Source
from .target import TargetWriter
from .transforms import TransformError, TransformFunc, coerce


class MigrationError(Exception):
    pass


@dataclass
class RunResult:
    processed: int = 0
    written: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    sample: list[dict[str, Any]] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


def load_state(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def transform_row(
    row: dict[str, Any],
    mapping: list[MappingColumn],
    transforms: dict[str, TransformFunc],
) -> tuple[Any, ...]:
    values: list[Any] = []
    for column in mapping:
        raw = row.get(column.source_column) if column.source_column else None
        if isinstance(raw, str) and not raw.strip():
            raw = None
        if raw is None and column.default is not None:
            raw = column.default
        if column.transform:
            function = transforms.get(column.transform)
            if function is None:
                raise TransformError(f"transform 不存在: {column.transform}")
            raw = function(raw, row)
        if raw is None and column.default is not None:
            raw = column.default
        if raw is None and column.required:
            raise TransformError(f"必填列为空: {column.target_column}")
        value = coerce(raw, column.target_type)
        if value is None and column.required:
            raise TransformError(f"必填列为空: {column.target_column}")
        values.append(value)
    return tuple(values)


def _display_row(
    values: tuple[Any, ...],
    mapping: list[MappingColumn],
) -> dict[str, Any]:
    return {
        column.target_column: _jsonable(value)
        for column, value in zip(mapping, values, strict=False)
    }


def run_migration(
    config: MigrationConfig,
    source: Source,
    mapping: list[MappingColumn],
    transforms: dict[str, TransformFunc],
    *,
    apply: bool,
    limit: int | None = None,
    reset_state: bool = False,
    batch_size: int | None = None,
) -> RunResult:
    state_path = config.run.state_file
    if reset_state and state_path.exists():
        state_path.unlink()

    state = load_state(state_path)
    is_file_source = config.source.type in {"csv", "excel"}
    cursor_column = config.source.cursor_column if not is_file_source else None

    start_row = int(state.get("row", 0)) if is_file_source else 0
    cursor = state.get("cursor") if cursor_column else None

    target = (
        TargetWriter(
            config.target,
            [column.target_column for column in mapping],
            config.run.key,
        )
        if apply
        else None
    )

    result = RunResult(state=state)
    batch: list[tuple[Any, ...]] = []
    last_row_index: int | None = None
    last_cursor: Any = None

    def flush() -> None:
        nonlocal batch, last_row_index, last_cursor
        if not batch:
            return
        if target is not None:
            target.write(batch)
            result.written += len(batch)
            if is_file_source and last_row_index is not None:
                result.state = {"row": last_row_index + 1}
            elif cursor_column and last_cursor is not None:
                result.state = {"cursor": _jsonable(last_cursor)}
            save_state(state_path, result.state)
        else:
            result.written += len(batch)
        batch = []

    try:
        for row_index, row in source.iter_rows(
            start_row=start_row,
            cursor=cursor,
        ):
            if limit is not None and result.processed >= limit:
                break
            result.processed += 1
            try:
                values = transform_row(row, mapping, transforms)
            except TransformError as exc:
                message = f"第 {row_index + 2} 行: {exc}"
                result.errors.append(message)
                if config.run.on_error == "stop":
                    raise MigrationError(message) from exc
                result.skipped += 1
                continue

            if len(result.sample) < config.run.sample_limit:
                result.sample.append(_display_row(values, mapping))

            batch.append(values)
            last_row_index = row_index
            if cursor_column:
                last_cursor = row.get(cursor_column)

            if len(batch) >= (batch_size or config.run.batch_size):
                flush()
        flush()
        if apply:
            save_state(state_path, result.state)
    finally:
        if target is not None:
            target.close()

    return result
