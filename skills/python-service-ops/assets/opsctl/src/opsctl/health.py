"""HTTP / TCP 健康检查。"""

from __future__ import annotations

import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class HealthResult:
    ok: bool
    detail: str
    latency_ms: int | None = None


def check_http(url: str, timeout: float = 2.0) -> HealthResult:
    start = time.monotonic()
    # 健康检查通常是 127.0.0.1，显式绕过 HTTP_PROXY，避免被代理环境变量带偏。
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(url, timeout=timeout) as response:
            elapsed = int((time.monotonic() - start) * 1000)
            code = getattr(response, "status", None) or response.getcode()
            if 200 <= code < 400:
                return HealthResult(True, f"HTTP {code}", elapsed)
            return HealthResult(False, f"HTTP {code}", elapsed)
    except urllib.error.HTTPError as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        return HealthResult(False, f"HTTP {exc.code}", elapsed)
    except Exception as exc:  # 网络错误类型很多，统一转为可读结果
        elapsed = int((time.monotonic() - start) * 1000)
        return HealthResult(False, f"不可达: {exc.__class__.__name__}", elapsed)


def check_port(host: str, port: int, timeout: float = 1.0) -> HealthResult:
    start = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            elapsed = int((time.monotonic() - start) * 1000)
            return HealthResult(True, "TCP 可连接", elapsed)
    except OSError as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        return HealthResult(False, f"TCP 不可达: {exc.__class__.__name__}", elapsed)
