from __future__ import annotations

from collections import Counter
from typing import Any

from .sources import Source

DISTINCT_LIMIT = 10_000


def profile_source(
    source: Source,
    *,
    sample_limit: int = 5,
    limit: int | None = None,
) -> dict[str, Any]:
    columns = source.columns
    nulls: Counter[str] = Counter()
    empties: Counter[str] = Counter()
    distinct: dict[str, set[str]] = {column: set() for column in columns}
    distinct_truncated: set[str] = set()
    samples: list[dict[str, Any]] = []
    row_count = 0

    for index, row in source.iter_rows():
        if limit is not None and index >= limit:
            break
        row_count += 1
        if len(samples) < sample_limit:
            samples.append({column: row.get(column) for column in columns})
        for column in columns:
            value = row.get(column)
            if value is None:
                nulls[column] += 1
                continue
            if isinstance(value, str) and not value.strip():
                empties[column] += 1
            key = str(value)
            if len(distinct[column]) < DISTINCT_LIMIT:
                distinct[column].add(key)
            else:
                distinct_truncated.add(column)

    total = source.count()
    return {
        "total_rows": total,
        "profiled_rows": row_count,
        "columns": columns,
        "nulls": dict(nulls),
        "empties": dict(empties),
        "distinct": {
            column: len(values) for column, values in distinct.items()
        },
        "distinct_truncated": sorted(distinct_truncated),
        "samples": samples,
    }


def format_profile_markdown(profile: dict[str, Any]) -> str:
    lines = [
        "# 源数据画像",
        "",
        f"- 总行数：{profile['total_rows'] if profile['total_rows'] is not None else '未知'}",
        f"- 已分析行数：{profile['profiled_rows']}",
        "",
        "| 列 | 空值 | 空字符串 | 去重值 | 备注 |",
        "|---|---:|---:|---:|---|",
    ]
    for column in profile["columns"]:
        note = "去重已截断" if column in profile["distinct_truncated"] else ""
        lines.append(
            f"| {column} | {profile['nulls'].get(column, 0)} | "
            f"{profile['empties'].get(column, 0)} | "
            f"{profile['distinct'].get(column, 0)} | {note} |"
        )

    lines.extend(["", "## 样例", ""])
    if not profile["samples"]:
        lines.append("没有样例数据。")
    else:
        for sample in profile["samples"]:
            lines.append(f"- `{sample}`")
    return "\n".join(lines) + "\n"
