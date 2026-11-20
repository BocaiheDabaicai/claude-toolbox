from __future__ import annotations

from typing import Any

from psycopg import sql

from .config import TargetConfig


class TargetError(Exception):
    pass


def build_insert_sql(
    target: TargetConfig,
    columns: list[str],
    key: tuple[str, ...],
) -> sql.Composable:
    if not columns:
        raise TargetError("没有目标列")
    table = sql.Identifier(target.schema, target.table)
    column_sql = sql.SQL(", ").join(sql.Identifier(column) for column in columns)
    placeholders = sql.SQL(", ").join(sql.Placeholder() * len(columns))
    query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        table,
        column_sql,
        placeholders,
    )

    if not key:
        return query

    conflict = sql.SQL(", ").join(sql.Identifier(column) for column in key)
    update_columns = [column for column in columns if column not in key]
    if update_columns:
        updates = sql.SQL(", ").join(
            sql.SQL("{} = EXCLUDED.{}").format(
                sql.Identifier(column),
                sql.Identifier(column),
            )
            for column in update_columns
        )
        return query + sql.SQL(" ON CONFLICT ({}) DO UPDATE SET {}").format(
            conflict,
            updates,
        )
    return query + sql.SQL(" ON CONFLICT ({}) DO NOTHING").format(conflict)


class TargetWriter:
    def __init__(
        self,
        target: TargetConfig,
        columns: list[str],
        key: tuple[str, ...],
    ) -> None:
        import psycopg

        self._conn = psycopg.connect(target.dsn)
        self._cursor = self._conn.cursor()
        self._query = build_insert_sql(target, columns, key)

    def write(self, rows: list[tuple[Any, ...]]) -> None:
        if not rows:
            return
        try:
            self._cursor.executemany(self._query, rows)
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def close(self) -> None:
        self._cursor.close()
        self._conn.close()
