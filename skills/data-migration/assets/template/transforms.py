"""项目自定义转换函数。

函数签名：fn(value, row) -> value。
在 mapping.csv 的 transform 列引用函数名。
"""

STATUS_MAP = {
    "1": "active",
    "0": "inactive",
    "正常": "active",
    "停用": "inactive",
    "ACTIVE": "active",
    "INACTIVE": "inactive",
}


def map_status(value, row):
    if value is None:
        return "active"
    text = str(value).strip()
    return STATUS_MAP.get(text, text.lower())


TRANSFORMS = {
    "map_status": map_status,
}
