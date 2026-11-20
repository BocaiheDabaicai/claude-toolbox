from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from urllib.parse import unquote, urlparse

from .config import MigrationConfig


class ReconcileError(Exception):
    pass


@dataclass
class ReconcileResult:
    name: str
    source_value: object
    target_value: object
    passed: bool
    detail: str = ""


def compare_values(source_value: object, target_value: object, tolerance: str) -> bool:
    try:
        source_number = Decimal(str(source_value))
        target_number = Decimal(str(target_value))
        limit = abs(Decimal(str(tolerance)))
    except (InvalidOperation, ValueError):
        return str(source_value) == str(target_value)
    return abs(source_number - target_number) <= limit


def _mysql_connection(dsn: str):
    try:
        import pymysql
    except ImportError as exc:
        raise ReconcileError(
            "MySQL 对账需要 pymysql，请安装：uv tool install '.[mysql]'"
        ) from exc

    parsed = urlparse(dsn)
    return pymysql.connect(
        host=parsed.hostname or "127.0.0.1",
        port=parsed.port or 3306,
        user=unquote(parsed.username or ""),
        password=unquote(parsed.password or ""),
        database=(parsed.path or "/").lstrip("/"),
        charset="utf8mb4",
    )


def run_reconcile(config: MigrationConfig) -> list[ReconcileResult]:
    if not config.reconcile_checks:
        return []
    if config.source.type not in {"postgres", "mysql"}:
        raise ReconcileError("SQL 对账只支持 postgres / mysql 源")

    import psycopg

    target_conn = psycopg.connect(config.target.dsn)
    if config.source.type == "postgres":
        source_conn = psycopg.connect(config.source.dsn)
        source_cursor = source_conn.cursor()
    else:
        source_conn = _mysql_connection(config.source.dsn or "")
        source_cursor = source_conn.cursor()

    target_cursor = target_conn.cursor()
    results: list[ReconcileResult] = []
    try:
        for check in config.reconcile_checks:
            source_cursor.execute(check.source_sql)
            source_row = source_cursor.fetchone()
            source_value = source_row[0] if source_row else None

            target_cursor.execute(check.target_sql)
            target_row = target_cursor.fetchone()
            target_value = target_row[0] if target_row else None

            passed = compare_values(source_value, target_value, check.tolerance)
            results.append(
                ReconcileResult(
                    name=check.name,
                    source_value=source_value,
                    target_value=target_value,
                    passed=passed,
                    detail="" if passed else "源/目标不一致",
                )
            )
    finally:
        source_cursor.close()
        target_cursor.close()
        source_conn.close()
        target_conn.close()
    return results


def format_reconcile_markdown(results: list[ReconcileResult]) -> str:
    lines = [
        "# 数据对账",
        "",
        "| 检查 | 源 | 目标 | 结果 | 备注 |",
        "|---|---|---|---|---|",
    ]
    if not results:
        lines.append("| - | - | - | - | 没有配置检查 |")
    for item in results:
        lines.append(
            f"| {item.name} | {item.source_value} | {item.target_value} | "
            f"{'PASS' if item.passed else 'FAIL'} | {item.detail} |"
        )
    return "\n".join(lines) + "\n"
