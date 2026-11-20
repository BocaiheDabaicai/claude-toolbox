from datetime import date
from decimal import Decimal

import pytest

from migration_kit.transforms import (
    TransformError,
    coerce,
    load_transforms,
    to_bool,
    to_date,
    trim,
)


def test_builtin_transforms():
    assert trim("  hello  ", {}) == "hello"
    assert trim("   ", {}) is None
    assert to_bool("是", {}) is True
    assert to_bool("0", {}) is False
    assert to_date("2026/11/20", {}) == date(2026, 11, 20)


def test_coerce():
    assert coerce("1", "bigint") == 1
    assert coerce("1.50", "numeric") == Decimal("1.50")
    assert coerce("x", "text") == "x"


def test_coerce_invalid():
    with pytest.raises(TransformError):
        coerce("abc", "bigint")


def test_load_custom_transform(workspace):
    transforms = load_transforms("transforms", workspace)

    function = transforms["normalize_company"]
    assert function(" 远山科技 ", {}) == "远山科技"
