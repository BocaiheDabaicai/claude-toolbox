from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

TARGET_TYPES = {
    "text",
    "varchar",
    "int",
    "bigint",
    "numeric",
    "boolean",
    "date",
    "timestamptz",
    "uuid",
}


class MappingError(Exception):
    pass


@dataclass(frozen=True)
class MappingColumn:
    target_column: str
    source_column: str
    target_type: str
    required: bool = False
    default: str | None = None
    transform: str | None = None


def _parse_bool(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "y", "是"}


def load_mapping(path: str | Path) -> list[MappingColumn]:
    mapping_path = Path(path)
    if not mapping_path.is_file():
        raise MappingError(f"映射文件不存在: {mapping_path}")

    with mapping_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        required_headers = {"target_column", "source_column", "target_type"}
        missing = required_headers - headers
        if missing:
            raise MappingError(f"映射缺少列: {', '.join(sorted(missing))}")

        columns: list[MappingColumn] = []
        seen_targets: set[str] = set()
        for line_number, row in enumerate(reader, start=2):
            target_column = (row.get("target_column") or "").strip()
            if not target_column:
                raise MappingError(f"第 {line_number} 行 target_column 为空")
            if target_column in seen_targets:
                raise MappingError(f"target_column 重复: {target_column}")
            seen_targets.add(target_column)

            target_type = (row.get("target_type") or "").strip().lower()
            if target_type not in TARGET_TYPES:
                raise MappingError(
                    f"第 {line_number} 行 target_type 不合法: {target_type or '空'}"
                )

            columns.append(
                MappingColumn(
                    target_column=target_column,
                    source_column=(row.get("source_column") or "").strip(),
                    target_type=target_type,
                    required=_parse_bool(row.get("required")),
                    default=(row.get("default") or "").strip() or None,
                    transform=(row.get("transform") or "").strip() or None,
                )
            )

    if not columns:
        raise MappingError("映射文件没有数据列")
    return columns


def validate_mapping(
    mapping: list[MappingColumn],
    source_columns: list[str],
    key_columns: tuple[str, ...],
    transform_names: set[str],
) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []
    source_set = set(source_columns)
    target_set = {column.target_column for column in mapping}

    for column in mapping:
        if column.source_column and column.source_column not in source_set:
            errors.append(
                f"{column.target_column}: 源列 {column.source_column!r} 不存在"
                f"（可用: {', '.join(source_columns)}）"
            )
        if not column.source_column and column.default is None and column.required:
            errors.append(
                f"{column.target_column}: 没有源列、没有默认值却被标记为必填"
            )
        if column.transform and column.transform not in transform_names:
            errors.append(
                f"{column.target_column}: transform {column.transform!r} 不存在"
            )

    for key in key_columns:
        if key not in target_set:
            errors.append(f"run.key 中的 {key!r} 不是映射目标列")
    if not key_columns:
        warnings.append("run.key 为空：写入不是幂等的，重复执行可能产生重复数据")

    return errors + [f"警告: {warning}" for warning in warnings]
