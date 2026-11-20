from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "ok"
    data: T | None = None


class Page(BaseModel, Generic[T]):
    rows: list[T]
    total: int
    page: int
    pageSize: int


def ok(data: object) -> dict[str, object]:
    return {"code": 200, "message": "ok", "data": data}
