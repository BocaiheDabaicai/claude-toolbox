#!/usr/bin/env python3
"""发布回归门禁：按 gate.toml 执行命令、HTTP 和文件检查。

用法：
  python gate.py --config gate.toml
  python gate.py --config gate.toml --only backend-tests
  python gate.py --config gate.toml --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ENV_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class GateError(Exception):
    pass


@dataclass(frozen=True)
class CheckConfig:
    name: str
    type: str
    enabled: bool = True
    command: str | None = None
    cwd: Path | None = None
    timeout: float = 300.0
    expect_exit: int = 0
    url: str | None = None
    expect_status: int = 200
    path: Path | None = None
    must_exist: bool = True


@dataclass(frozen=True)
class GateConfig:
    project_name: str
    report: Path | None
    checks: tuple[CheckConfig, ...]
    path: Path
    base_dir: Path


@dataclass
class CheckResult:
    name: str
    type: str
    passed: bool
    detail: str
    duration: float
    output: str = ""


def _expand(value):
    if isinstance(value, str):

        def replace(match: re.Match[str]) -> str:
            name = match.group(1)
            if name not in os.environ:
                raise GateError(f"环境变量未设置: {name}")
            return os.environ[name]

        return ENV_RE.sub(replace, value)
    if isinstance(value, list):
        return [_expand(item) for item in value]
    if isinstance(value, dict):
        return {key: _expand(item) for key, item in value.items()}
    return value


def _str(data: dict, key: str, *, required: bool = True) -> str | None:
    value = data.get(key)
    if value is None:
        if required:
            raise GateError(f"缺少配置: {key}")
        return None
    if not isinstance(value, str) or not value.strip():
        raise GateError(f"配置必须是非空字符串: {key}")
    return value.strip()


def _int(data: dict, key: str, default: int) -> int:
    value = data.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool):
        raise GateError(f"配置必须是整数: {key}")
    return value


def _float(data: dict, key: str, default: float) -> float:
    value = data.get(key, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise GateError(f"配置必须是数字: {key}")
    return float(value)


def load_config(path: str | Path) -> GateConfig:
    config_path = Path(path).resolve()
    try:
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GateError(f"配置文件不存在: {config_path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise GateError(f"TOML 解析失败: {exc}") from exc

    data = _expand(raw)
    base = config_path.parent
    project = data.get("project", {})
    if not isinstance(project, dict):
        raise GateError("[project] 必须是表")
    project_name = _str(project, "name", required=False) or "project"
    report_value = _str(project, "report", required=False)
    report = (base / report_value).resolve() if report_value else None

    checks_raw = data.get("checks")
    if not isinstance(checks_raw, list) or not checks_raw:
        raise GateError("至少需要一个 [[checks]]")

    checks: list[CheckConfig] = []
    seen_names: set[str] = set()
    for index, item in enumerate(checks_raw):
        if not isinstance(item, dict):
            raise GateError(f"checks[{index}] 必须是表")
        name = _str(item, "name") or f"check-{index + 1}"
        if name in seen_names:
            raise GateError(f"check 名称重复: {name}")
        seen_names.add(name)

        check_type = (_str(item, "type") or "").lower()
        if check_type not in {"command", "http", "file"}:
            raise GateError(f"{name}: type 只允许 command / http / file")

        enabled = item.get("enabled", True)
        if not isinstance(enabled, bool):
            raise GateError(f"{name}: enabled 必须是布尔值")

        if check_type == "command":
            command = _str(item, "command") or ""
            cwd_value = _str(item, "cwd", required=False)
            cwd = (base / cwd_value).resolve() if cwd_value else None
            checks.append(
                CheckConfig(
                    name=name,
                    type=check_type,
                    enabled=enabled,
                    command=command,
                    cwd=cwd,
                    timeout=_float(item, "timeout", 300.0),
                    expect_exit=_int(item, "expect_exit", 0),
                )
            )
        elif check_type == "http":
            checks.append(
                CheckConfig(
                    name=name,
                    type=check_type,
                    enabled=enabled,
                    url=_str(item, "url") or "",
                    expect_status=_int(item, "expect_status", 200),
                    timeout=_float(item, "timeout", 10.0),
                )
            )
        else:
            path_value = _str(item, "path") or ""
            checks.append(
                CheckConfig(
                    name=name,
                    type=check_type,
                    enabled=enabled,
                    path=(base / path_value).resolve(),
                    must_exist=bool(item.get("must_exist", True)),
                )
            )

    return GateConfig(
        project_name=project_name,
        report=report,
        checks=tuple(checks),
        path=config_path,
        base_dir=base,
    )


def _tail(text: str, limit: int = 3000) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else "..." + text[-limit:]


def run_check(check: CheckConfig) -> CheckResult:
    started = time.perf_counter()
    if check.type == "command":
        if not check.command:
            return CheckResult(check.name, check.type, False, "缺少 command", 0.0)
        if check.cwd is not None and not check.cwd.is_dir():
            return CheckResult(
                check.name,
                check.type,
                False,
                f"cwd 不存在: {check.cwd}",
                time.perf_counter() - started,
            )
        try:
            process = subprocess.run(
                check.command,
                shell=True,
                cwd=check.cwd,
                timeout=check.timeout,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            return CheckResult(
                check.name,
                check.type,
                False,
                f"超时 {check.timeout:g}s",
                time.perf_counter() - started,
            )
        duration = time.perf_counter() - started
        passed = process.returncode == check.expect_exit
        detail = f"exit {process.returncode}"
        if not passed:
            detail += f", 期望 {check.expect_exit}"
        output = _tail((process.stdout or "") + (process.stderr or ""))
        return CheckResult(check.name, check.type, passed, detail, duration, output)

    if check.type == "http":
        if not check.url:
            return CheckResult(check.name, check.type, False, "缺少 url", 0.0)
        try:
            with urllib.request.urlopen(check.url, timeout=check.timeout) as response:
                status = response.status
        except urllib.error.HTTPError as exc:
            status = exc.code
        except Exception as exc:
            return CheckResult(
                check.name,
                check.type,
                False,
                f"请求失败: {exc.__class__.__name__}",
                time.perf_counter() - started,
            )
        duration = time.perf_counter() - started
        passed = status == check.expect_status
        detail = f"HTTP {status}"
        if not passed:
            detail += f", 期望 {check.expect_status}"
        return CheckResult(check.name, check.type, passed, detail, duration)

    if check.path is None:
        return CheckResult(check.name, check.type, False, "缺少 path", 0.0)
    exists = check.path.exists()
    passed = exists == check.must_exist
    detail = "存在" if exists else "不存在"
    if not passed:
        detail += f", 期望{'存在' if check.must_exist else '不存在'}"
    return CheckResult(
        check.name,
        check.type,
        passed,
        detail,
        time.perf_counter() - started,
    )


def format_report(config: GateConfig, results: list[CheckResult]) -> str:
    passed = sum(1 for result in results if result.passed)
    lines = [
        "# 回归门禁报告",
        "",
        f"- 项目：{config.project_name}",
        f"- 时间：{datetime.now().isoformat(timespec='seconds')}",
        f"- 结果：{passed}/{len(results)} 通过",
        "",
        "| 检查 | 类型 | 结果 | 耗时 | 详情 |",
        "|---|---|---|---:|---|",
    ]
    for result in results:
        lines.append(
            f"| {result.name} | {result.type} | "
            f"{'PASS' if result.passed else 'FAIL'} | "
            f"{result.duration:.1f}s | {result.detail} |"
        )
    failures = [result for result in results if not result.passed and result.output]
    if failures:
        lines.extend(["", "## 失败输出", ""])
        for result in failures:
            lines.append(f"### {result.name}")
            lines.append("")
            lines.append("```text")
            lines.append(result.output)
            lines.append("```")
            lines.append("")
    return "\n".join(lines) + "\n"


def run_gate(
    config: GateConfig,
    *,
    only: list[str] | None = None,
    fail_fast: bool = False,
    dry_run: bool = False,
) -> list[CheckResult]:
    selected = [
        check
        for check in config.checks
        if check.enabled and (not only or check.name in only)
    ]
    if only and not selected:
        raise GateError(f"没有匹配的检查: {', '.join(only)}")

    if dry_run:
        for check in selected:
            if check.type == "command":
                target = f"{check.command} (cwd={check.cwd or config.base_dir})"
            elif check.type == "http":
                target = f"{check.url} -> {check.expect_status}"
            else:
                target = str(check.path)
            print(f"[DRY] {check.type} {check.name}: {target}")
        return []

    results: list[CheckResult] = []
    for check in selected:
        result = run_check(check)
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {check.name} ({result.duration:.1f}s) {result.detail}")
        if not result.passed and result.output:
            print(result.output, file=sys.stderr)
        if not result.passed and fail_fast:
            break

    passed = sum(1 for result in results if result.passed)
    print(f"summary: {passed}/{len(results)} passed")
    return results


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError, OSError):
                pass

    parser = argparse.ArgumentParser(description="发布回归门禁")
    parser.add_argument("--config", required=True, help="gate.toml")
    parser.add_argument("--only", action="append", help="只执行指定名称的检查")
    parser.add_argument("--fail-fast", action="store_true", help="首个失败后停止")
    parser.add_argument("--dry-run", action="store_true", help="只打印检查，不执行")
    parser.add_argument("--report", help="覆盖报告输出路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果")
    parser.add_argument("--list", action="store_true", help="列出检查")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except GateError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    if args.list:
        for check in config.checks:
            print(f"{check.type:8} {check.name}")
        return 0

    try:
        results = run_gate(
            config,
            only=args.only,
            fail_fast=args.fail_fast,
            dry_run=args.dry_run,
        )
    except GateError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        return 0

    report_path = Path(args.report).resolve() if args.report else config.report
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            format_report(config, results),
            encoding="utf-8",
        )
        print(f"report: {report_path}")

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "name": result.name,
                        "type": result.type,
                        "passed": result.passed,
                        "detail": result.detail,
                        "duration": round(result.duration, 3),
                    }
                    for result in results
                ],
                ensure_ascii=False,
                indent=2,
            )
        )

    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
