from typing import Any


class ApiError(Exception):
    """业务错误：HTTP 状态码与响应 code 保持一致。"""

    def __init__(
        self,
        code: int,
        message: str,
        *,
        status_code: int | None = None,
        details: Any = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code or code
        self.details = details
        super().__init__(message)
