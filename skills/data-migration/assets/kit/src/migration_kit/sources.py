from __future__ import annotations

import csv
from collections.abc import Iterator
from typing import Any, Protocol
from urllib.parse import unquote, urlparse

from psycopg import sql

from .config import SourceConfig


class SourceError(Exception):
    pass


class Source(Protocol):
    columns: list[str]

    def iter_rows(
        self,
        *,
        start_row: int = 0,
        cursor: Any = None,
    ) -> Iterator[tuple[int, dict[str, Any]]]: ...

    def count(self) -> int | None: ...

    def close(self) -> None: ...


class CSVSource:
    def __init__(self, config: SourceConfig) -> None:
        if not config.path or not config.path.is_file():
            raise SourceError(f"CSV 文件不存在: {config.path}")
        self.config = config
        self._handle = config.path.open(
            "r",
            encoding=config.encoding,
            newline="",
        )
        self._reader = csv.DictReader(self._handle, delimiter=config.delimiter)
        if not self._reader.fieldnames:
            self._handle.close()
            raise SourceError("CSV 没有表头")
        self.columns = list(self._reader.fieldnames)

    def iter_rows(
        self,
        *,
        start_row: int = 0,
        cursor: Any = None,
    ) -> Iterator[tuple[int, dict[str, Any]]]:
        for index, row in enumerate(self._reader):
            if index < start_row:
                continue
            yield index, dict(row)

    def count(self) -> int | None:
        if not self.config.path:
            return None
        with self.config.path.open(
            "r",
            encoding=self.config.encoding,
            newline="",
        ) as handle:
            reader = csv.DictReader(handle, delimiter=self.config.delimiter)
            return sum(1 for _ in reader)

    def close(self) -> None:
        self._handle.close()


class ExcelSource:
    def __init__(self, config: SourceConfig) -> None:
        if not config.path or not config.path.is_file():
            raise SourceError(f"Excel 文件不存在: {config.path}")
        try:
            import openpyxl
        except ImportError as exc:
            raise SourceError(
                "Excel 源需要 openpyxl，请安装：uv tool install '.[excel]'"
            ) from exc

        self._workbook = openpyxl.load_workbook(
            config.path,
            read_only=True,
            data_only=True,
        )
        self._sheet = (
            self._workbook[config.sheet]
            if config.sheet
            else self._workbook.active
        )
        self._rows = self._sheet.iter_rows(values_only=True)
        headers = next(self._rows, None)
        if not headers:
            raise SourceError("Excel 没有表头")
        self.columns = [
            str(value).strip() if value is not None else f"column_{index + 1}"
            for index, value in enumerate(headers)
        ]
        if len(set(self.columns)) != len(self.columns):
            raise SourceError("Excel 表头存在重复列名")

    def iter_rows(
        self,
        *,
        start_row: int = 0,
        cursor: Any = None,
    ) -> Iterator[tuple[int, dict[str, Any]]]:
        for index, values in enumerate(self._rows):
            if index < start_row:
                continue
            yield index, dict(zip(self.columns, values, strict=False))

    def count(self) -> int | None:
        max_row = self._sheet.max_row or 1
        return max(max_row - 1, 0)

    def close(self) -> None:
        self._workbook.close()


class PostgresSource:
    def __init__(self, config: SourceConfig) -> None:
        if not config.dsn or not config.table:
            raise SourceError("PostgreSQL 源需要 dsn 和 table")
        import psycopg

        self.config = config
        self._conn = psycopg.connect(config.dsn)
        self._table = sql.Identifier(config.schema, config.table)
        with self._conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("SELECT * FROM {} LIMIT 0").format(self._table)
            )
            self.columns = [item.name for item in cursor.description or []]
        if config.cursor_column and config.cursor_column not in self.columns:
            raise SourceError(
                f"cursor_column 不存在: {config.cursor_column}"
            )

    def _base_query(self) -> sql.Composable:
        return sql.SQL("SELECT * FROM {}").format(self._table)

    def _where_clause(
        self,
        cursor_value: Any = None,
    ) -> tuple[sql.Composable, list[Any]]:
        conditions: list[sql.Composable] = []
        params: list[Any] = []
        if self.config.where:
            conditions.append(sql.SQL(self.config.where))
        if self.config.cursor_column and cursor_value is not None:
            conditions.append(
                sql.SQL("{} > %s").format(
                    sql.Identifier(self.config.cursor_column)
                )
            )
            params.append(cursor_value)
        if not conditions:
            return sql.SQL(""), params
        return (
            sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions),
            params,
        )

    def iter_rows(
        self,
        *,
        start_row: int = 0,
        cursor: Any = None,
    ) -> Iterator[tuple[int, dict[str, Any]]]:
        index = 0
        if self.config.cursor_column:
            current = cursor
            batch_size = 1000
            while True:
                where, params = self._where_clause(current)
                query = (
                    self._base_query()
                    + where
                    + sql.SQL(" ORDER BY {}").format(
                        sql.Identifier(self.config.cursor_column)
                    )
                    + sql.SQL(" LIMIT %s")
                )
                with self._conn.cursor() as db_cursor:
                    db_cursor.execute(query, [*params, batch_size])
                    rows = db_cursor.fetchall()
                if not rows:
                    break
                for row in rows:
                    if index >= start_row:
                        yield index, dict(zip(self.columns, row, strict=False))
                    index += 1
                current = rows[-1][self.columns.index(self.config.cursor_column)]
                if len(rows) < batch_size:
                    break
            return

        with self._conn.cursor(name="migration_source") as db_cursor:
            db_cursor.itersize = 1000
            where, params = self._where_clause()
            db_cursor.execute(self._base_query() + where, params)
            while True:
                rows = db_cursor.fetchmany(1000)
                if not rows:
                    break
                for row in rows:
                    if index >= start_row:
                        yield index, dict(zip(self.columns, row, strict=False))
                    index += 1

    def count(self) -> int | None:
        where, params = self._where_clause()
        query = sql.SQL("SELECT count(*) FROM {}").format(self._table) + where
        with self._conn.cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return int(row[0]) if row else 0

    def close(self) -> None:
        self._conn.close()


def _quote_mysql(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


class MySQLSource:
    def __init__(self, config: SourceConfig) -> None:
        if not config.dsn or not config.table:
            raise SourceError("MySQL 源需要 dsn 和 table")
        try:
            import pymysql
        except ImportError as exc:
            raise SourceError(
                "MySQL 源需要 pymysql，请安装：uv tool install '.[mysql]'"
            ) from exc

        parsed = urlparse(config.dsn)
        if parsed.scheme not in {"mysql", "mysql+pymysql"}:
            raise SourceError("MySQL dsn 应为 mysql://user:pass@host:port/db")
        self.config = config
        self._table = (
            f"{_quote_mysql(config.schema)}.{_quote_mysql(config.table)}"
        )
        self._conn = pymysql.connect(
            host=parsed.hostname or "127.0.0.1",
            port=parsed.port or 3306,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            database=(parsed.path or "/").lstrip("/"),
            charset="utf8mb4",
        )
        with self._conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self._table} LIMIT 0")
            self.columns = [item[0] for item in cursor.description or []]
        if config.cursor_column and config.cursor_column not in self.columns:
            raise SourceError(
                f"cursor_column 不存在: {config.cursor_column}"
            )

    def _where_clause(
        self,
        cursor_value: Any = None,
    ) -> tuple[str, list[Any]]:
        conditions: list[str] = []
        params: list[Any] = []
        if self.config.where:
            conditions.append(self.config.where)
        if self.config.cursor_column and cursor_value is not None:
            conditions.append(f"{_quote_mysql(self.config.cursor_column)} > %s")
            params.append(cursor_value)
        if not conditions:
            return "", params
        return " WHERE " + " AND ".join(conditions), params

    def iter_rows(
        self,
        *,
        start_row: int = 0,
        cursor: Any = None,
    ) -> Iterator[tuple[int, dict[str, Any]]]:
        index = 0
        batch_size = 1000
        if self.config.cursor_column:
            current = cursor
            while True:
                where, params = self._where_clause(current)
                query = (
                    f"SELECT * FROM {self._table}{where} "
                    f"ORDER BY {_quote_mysql(self.config.cursor_column)} LIMIT %s"
                )
                with self._conn.cursor() as db_cursor:
                    db_cursor.execute(query, [*params, batch_size])
                    rows = db_cursor.fetchall()
                if not rows:
                    break
                for row in rows:
                    if index >= start_row:
                        yield index, dict(zip(self.columns, row, strict=False))
                    index += 1
                current = rows[-1][self.columns.index(self.config.cursor_column)]
                if len(rows) < batch_size:
                    break
            return

        with self._conn.cursor() as db_cursor:
            where, params = self._where_clause()
            db_cursor.execute(f"SELECT * FROM {self._table}{where}", params)
            while True:
                rows = db_cursor.fetchmany(batch_size)
                if not rows:
                    break
                for row in rows:
                    if index >= start_row:
                        yield index, dict(zip(self.columns, row, strict=False))
                    index += 1

    def count(self) -> int | None:
        where, params = self._where_clause()
        with self._conn.cursor() as cursor:
            cursor.execute(f"SELECT count(*) FROM {self._table}{where}", params)
            row = cursor.fetchone()
            return int(row[0]) if row else 0

    def close(self) -> None:
        self._conn.close()


def open_source(config: SourceConfig) -> Source:
    if config.type == "csv":
        return CSVSource(config)
    if config.type == "excel":
        return ExcelSource(config)
    if config.type == "postgres":
        return PostgresSource(config)
    if config.type == "mysql":
        return MySQLSource(config)
    raise SourceError(f"不支持的 source.type: {config.type}")
