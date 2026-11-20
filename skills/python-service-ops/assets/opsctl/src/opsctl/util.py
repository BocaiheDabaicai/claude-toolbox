"""通用工具：错误类型、命令执行、颜色和校验。"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class OpsError(Exception):
    """opsctl 的基础错误。"""


class ManifestError(OpsError):
    """project.toml 不合法。"""


class SystemdError(OpsError):
    """systemd 操作失败。"""


def validate_slug(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{field} 不能为空")
    value = value.strip()
    if not SLUG_RE.match(value):
        raise ManifestError(
            f"{field}={value!r} 不合法：只允许小写字母、数字和中划线，且必须以字母或数字开头"
        )
    return value


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def is_root() -> bool:
    geteuid = getattr(os, "geteuid", None)
    return bool(geteuid and geteuid() == 0)


def which(command: str) -> str | None:
    return shutil.which(command)


def require_systemd() -> None:
    if not is_linux():
        raise SystemdError("systemd 管理只支持 Linux；当前系统不是 Linux")
    if not which("systemctl"):
        raise SystemdError("找不到 systemctl，请确认系统使用 systemd")


def run(
    args: Sequence[str],
    *,
    check: bool = True,
    capture: bool = True,
    dry_run: bool = False,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """执行命令；dry_run 时只打印，不执行。"""
    printable = " ".join(shlex.quote(str(item)) for item in args)
    if dry_run:
        print(f"+ {printable}")
        return subprocess.CompletedProcess(args, 0, "", "")
    try:
        return subprocess.run(
            [str(item) for item in args],
            check=check,
            capture_output=capture,
            text=True,
            env=env,
            cwd=cwd,
        )
    except FileNotFoundError as exc:
        raise OpsError(f"命令不存在: {args[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        suffix = f"\n{detail}" if detail else ""
        raise OpsError(f"命令执行失败: {printable}{suffix}") from exc


def print_json(data: object) -> None:
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


@dataclass(frozen=True)
class Color:
    enabled: bool

    def _wrap(self, code: str, text: str) -> str:
        if not self.enabled:
            return text
        return f"\033[{code}m{text}\033[0m"

    def green(self, text: str) -> str:
        return self._wrap("32", text)

    def red(self, text: str) -> str:
        return self._wrap("31", text)

    def yellow(self, text: str) -> str:
        return self._wrap("33", text)

    def dim(self, text: str) -> str:
        return self._wrap("2", text)

    def bold(self, text: str) -> str:
        return self._wrap("1", text)


def color_enabled(no_color: bool = False) -> bool:
    if no_color or os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def human_join(items: Iterable[str], sep: str = ", ") -> str:
    return sep.join(items)
