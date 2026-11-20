from __future__ import annotations

import importlib
import importlib.util
import re
import uuid
from collections.abc import Callable, Mapping
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

TransformFunc = Callable[[Any, Mapping[str, Any]], Any]


class TransformError(Exception):
    pass


def _none_if_empty(value: Any) -> Any:
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def trim(value: Any, _row: Mapping[str, Any]) -> Any:
    return _none_if_empty(value)


def lower(value: Any, _row: Mapping[str, Any]) -> Any:
    value = _none_if_empty(value)
    return value.lower() if isinstance(value, str) else value


def upper(value: Any, _row: Mapping[str, Any]) -> Any:
    value = _none_if_empty(value)
    return value.upper() if isinstance(value, str) else value


def digits(value: Any, _row: Mapping[str, Any]) -> Any:
    value = _none_if_empty(value)
    if value is None:
        return None
    digits_only = re.sub(r"\D", "", str(value))
    return digits_only or None


def to_decimal(value: Any, _row: Mapping[str, Any]) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise TransformError(f"无法转成 numeric: {value!r}") from exc
    if not result.is_finite():
        raise TransformError(f"numeric 不允许 NaN/Infinity: {value!r}")
    return result


def to_bool(value: Any, _row: Mapping[str, Any]) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "是", "正常", "active"}:
        return True
    if text in {"0", "false", "no", "n", "否", "停用", "inactive"}:
        return False
    raise TransformError(f"无法转成 boolean: {value!r}")


def to_date(value: Any, _row: Mapping[str, Any]) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for parser in (
        date.fromisoformat,
        lambda item: datetime.strptime(item, "%Y/%m/%d").date(),
        lambda item: datetime.strptime(item, "%Y%m%d").date(),
        lambda item: datetime.strptime(item, "%Y.%m.%d").date(),
    ):
        try:
            return parser(text)
        except ValueError:
            continue
    raise TransformError(f"无法转成 date: {value!r}")


def to_datetime(value: Any, _row: Mapping[str, Any]) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=UTC)
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
            try:
                parsed = datetime.strptime(text, fmt)
                break
            except ValueError:
                continue
        else:
            raise TransformError(f"无法转成 datetime: {value!r}") from None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def to_uuid(value: Any, _row: Mapping[str, Any]) -> str:
    try:
        return str(uuid.UUID(str(value).strip()))
    except (ValueError, AttributeError) as exc:
        raise TransformError(f"无法转成 uuid: {value!r}") from exc


def identity(value: Any, _row: Mapping[str, Any]) -> Any:
    return value


BUILTIN_TRANSFORMS: dict[str, TransformFunc] = {
    "trim": trim,
    "lower": lower,
    "upper": upper,
    "digits": digits,
    "decimal": to_decimal,
    "bool": to_bool,
    "date": to_date,
    "datetime": to_datetime,
    "uuid": to_uuid,
    "identity": identity,
}


def load_transforms(module_name: str, base_dir: Path) -> dict[str, TransformFunc]:
    transforms = dict(BUILTIN_TRANSFORMS)
    if not module_name:
        return transforms

    module_path = base_dir / f"{module_name.replace('.', '/')}.py"
    module = None
    if module_path.is_file():
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
    else:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            module = None

    if module is not None:
        custom = getattr(module, "TRANSFORMS", {})
        if not isinstance(custom, dict):
            raise TransformError(f"{module_name}.TRANSFORMS 必须是 dict")
        for name, function in custom.items():
            if not callable(function):
                raise TransformError(f"自定义 transform 不可调用: {name}")
            transforms[name] = function
    return transforms


def coerce(value: Any, target_type: str) -> Any:
    if value is None:
        return None
    if target_type in {"text", "varchar"}:
        text = str(value)
        return text if text.strip() else None
    if target_type in {"int", "bigint"}:
        try:
            return int(str(value).strip())
        except (TypeError, ValueError) as exc:
            raise TransformError(f"无法转成 {target_type}: {value!r}") from exc
    if target_type == "numeric":
        return to_decimal(value, {})
    if target_type == "boolean":
        return to_bool(value, {})
    if target_type == "date":
        return to_date(value, {})
    if target_type == "timestamptz":
        return to_datetime(value, {})
    if target_type == "uuid":
        return to_uuid(value, {})
    raise TransformError(f"未知 target_type: {target_type}")
