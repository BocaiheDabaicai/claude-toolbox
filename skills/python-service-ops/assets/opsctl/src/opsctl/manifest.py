"""project.toml 的加载、校验与数据类型。"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .util import ManifestError, validate_slug

RESTART_VALUES = {"no", "always", "on-failure"}
KINDS = {"node", "python", "command"}
PROJECT_TYPES = {"nuxt", "vue-fastapi", "custom"}


@dataclass(frozen=True)
class HealthConfig:
    path: str = "/healthz"
    timeout: float = 2.0


@dataclass(frozen=True)
class ServiceConfig:
    name: str
    command: str
    kind: str = "command"
    working_dir: str | None = None
    port: int | None = None
    health: str | None = None
    systemd: str | None = None
    restart: str = "on-failure"
    restart_sec: int = 3
    environment: dict[str, str] = field(default_factory=dict)
    oneshot: bool = False
    before: tuple[str, ...] = ()
    timeout_stop_sec: int = 15

    def unit_name(self, project_slug: str) -> str:
        return self.systemd or f"{project_slug}-{self.name}.service"

    def health_url(self, project: "ProjectConfig") -> str | None:
        if self.health:
            return self.health
        if not self.port:
            return None
        path = project.health.path
        if not path.startswith("/"):
            path = "/" + path
        return f"http://127.0.0.1:{self.port}{path}"


@dataclass(frozen=True)
class ProjectConfig:
    slug: str
    name: str
    manifest_path: Path
    project_dir: Path
    root: Path
    type: str = "custom"
    env_file: Path | None = None
    user: str | None = None
    group: str | None = None
    description: str | None = None
    health: HealthConfig = field(default_factory=HealthConfig)
    after: tuple[str, ...] = ()
    services: tuple[ServiceConfig, ...] = ()

    @property
    def target_name(self) -> str:
        return f"{self.slug}.target"

    def service_by_name(self, name: str) -> ServiceConfig | None:
        return next((service for service in self.services if service.name == name), None)

    def unit_map(self) -> dict[str, str]:
        return {service.name: service.unit_name(self.slug) for service in self.services}


def _as_str(value: Any, field_name: str, *, required: bool = True) -> str | None:
    if value is None:
        if required:
            raise ManifestError(f"{field_name} 不能为空")
        return None
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{field_name} 必须是非空字符串")
    return value.strip()


def _as_int(
    value: Any,
    field_name: str,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ManifestError(f"{field_name} 必须是整数")
    if minimum is not None and value < minimum:
        raise ManifestError(f"{field_name} 不能小于 {minimum}")
    if maximum is not None and value > maximum:
        raise ManifestError(f"{field_name} 不能大于 {maximum}")
    return value


def _as_float(value: Any, field_name: str, *, minimum: float | None = None) -> float | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ManifestError(f"{field_name} 必须是数字")
    result = float(value)
    if minimum is not None and result < minimum:
        raise ManifestError(f"{field_name} 不能小于 {minimum}")
    return result


def _as_str_list(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ManifestError(f"{field_name} 必须是字符串数组")
    return tuple(item.strip() for item in value)


def load_project(manifest_path: Path) -> ProjectConfig:
    manifest_path = manifest_path.resolve()
    if not manifest_path.is_file():
        raise ManifestError(f"manifest 不存在: {manifest_path}")
    try:
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ManifestError(f"TOML 解析失败: {manifest_path}: {exc}") from exc

    project_data = data.get("project")
    if not isinstance(project_data, dict):
        raise ManifestError(f"{manifest_path}: 缺少 [project]")

    slug = validate_slug(_as_str(project_data.get("slug"), "[project].slug") or "", "[project].slug")
    name = _as_str(project_data.get("name"), "[project].name") or ""

    # 约定：<project-dir>/ops/project.toml
    project_dir = manifest_path.parent.parent
    root_value = _as_str(project_data.get("root"), "[project].root", required=False) or "."
    root = (project_dir / root_value).resolve()

    type_value = (_as_str(project_data.get("type"), "[project].type", required=False) or "custom").lower()
    if type_value not in PROJECT_TYPES:
        raise ManifestError("[project].type 只允许 nuxt / vue-fastapi / custom")

    env_value = _as_str(project_data.get("env_file"), "[project].env_file", required=False)
    env_file = (root / env_value).resolve() if env_value else None

    health_data = project_data.get("health") or {}
    if not isinstance(health_data, dict):
        raise ManifestError("[project.health] 必须是表")
    health = HealthConfig(
        path=_as_str(health_data.get("path"), "[project.health].path", required=False) or "/healthz",
        timeout=_as_float(health_data.get("timeout"), "[project.health].timeout", minimum=0.1) or 2.0,
    )

    after = _as_str_list(project_data.get("after"), "[project].after")

    services_data = data.get("services")
    if not isinstance(services_data, list) or not services_data:
        raise ManifestError(f"{manifest_path}: 至少需要一个 [[services]]")

    services: list[ServiceConfig] = []
    seen: set[str] = set()
    for index, service_data in enumerate(services_data):
        prefix = f"[[services]][{index}]"
        if not isinstance(service_data, dict):
            raise ManifestError(f"{prefix} 必须是表")

        service_name = validate_slug(
            _as_str(service_data.get("name"), f"{prefix}.name") or "",
            f"{prefix}.name",
        )
        if service_name in seen:
            raise ManifestError(f"服务名重复: {service_name}")
        seen.add(service_name)

        command = _as_str(service_data.get("command"), f"{prefix}.command") or ""
        if "\n" in command or "\r" in command:
            raise ManifestError(f"{prefix}.command 不能包含换行")
        kind = (_as_str(service_data.get("kind"), f"{prefix}.kind", required=False) or "command").lower()
        if kind not in KINDS:
            raise ManifestError(f"{prefix}.kind 只允许 node / python / command")

        restart = (
            _as_str(service_data.get("restart"), f"{prefix}.restart", required=False) or "on-failure"
        ).lower()
        if restart not in RESTART_VALUES:
            raise ManifestError(f"{prefix}.restart 只允许 no / always / on-failure")

        oneshot = bool(service_data.get("oneshot", False))
        if oneshot:
            # 一次性任务（如迁移）不应被 systemd 反复拉起。
            restart = "no"

        environment_data = service_data.get("environment") or {}
        if not isinstance(environment_data, dict) or any(
            not isinstance(key, str) or not isinstance(value, (str, int, float, bool))
            for key, value in environment_data.items()
        ):
            raise ManifestError(f"{prefix}.environment 必须是字符串键值表")
        environment = {
            str(key): ("true" if value is True else "false" if value is False else str(value))
            for key, value in environment_data.items()
        }

        health_url = _as_str(service_data.get("health"), f"{prefix}.health", required=False)
        if health_url and not health_url.startswith(("http://", "https://")):
            raise ManifestError(f"{prefix}.health 必须是 http:// 或 https:// 开头的完整 URL")

        working_dir_value = _as_str(service_data.get("working_dir"), f"{prefix}.working_dir", required=False)
        working_dir = str((root / working_dir_value).resolve()) if working_dir_value else None

        systemd_name = _as_str(service_data.get("systemd"), f"{prefix}.systemd", required=False)
        if systemd_name:
            if not systemd_name.endswith(".service"):
                raise ManifestError(f"{prefix}.systemd 必须以 .service 结尾")
            if "/" in systemd_name or "\\" in systemd_name or ".." in systemd_name:
                raise ManifestError(f"{prefix}.systemd 不能包含路径分隔符或 ..")

        services.append(
            ServiceConfig(
                name=service_name,
                command=command,
                kind=kind,
                working_dir=working_dir,
                port=_as_int(service_data.get("port"), f"{prefix}.port", minimum=1, maximum=65535),
                health=health_url,
                systemd=systemd_name,
                restart=restart,
                restart_sec=_as_int(service_data.get("restart_sec"), f"{prefix}.restart_sec", minimum=1) or 3,
                environment=environment,
                oneshot=oneshot,
                before=_as_str_list(service_data.get("before"), f"{prefix}.before"),
                timeout_stop_sec=_as_int(
                    service_data.get("timeout_stop_sec"),
                    f"{prefix}.timeout_stop_sec",
                    minimum=1,
                )
                or 15,
            )
        )

    service_names = {service.name for service in services}
    for service in services:
        for dependency in service.before:
            if dependency == service.name:
                raise ManifestError(f"服务 {service.name} 不能 before 自己")
            if dependency not in service_names:
                raise ManifestError(f"服务 {service.name} 的 before 引用了不存在的服务: {dependency}")

    return ProjectConfig(
        slug=slug,
        name=name,
        manifest_path=manifest_path,
        project_dir=project_dir,
        root=root,
        type=type_value,
        env_file=env_file,
        user=_as_str(project_data.get("user"), "[project].user", required=False),
        group=_as_str(project_data.get("group"), "[project].group", required=False),
        description=_as_str(project_data.get("description"), "[project].description", required=False),
        health=health,
        after=after,
        services=tuple(services),
    )
