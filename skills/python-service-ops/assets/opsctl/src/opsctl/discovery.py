"""在工作区中发现所有 ops/project.toml。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .manifest import ProjectConfig, load_project
from .util import ManifestError

DEFAULT_EXCLUDES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".nuxt",
    ".output",
    ".next",
    "dist",
    "build",
    "coverage",
}


@dataclass
class DiscoveryResult:
    projects: list[ProjectConfig] = field(default_factory=list)
    errors: list[tuple[Path, str]] = field(default_factory=list)


def discover(root: Path, max_depth: int = 4) -> DiscoveryResult:
    root = root.resolve()
    result = DiscoveryResult()
    if not root.is_dir():
        result.errors.append((root, "工作区目录不存在"))
        return result

    seen: set[Path] = set()

    def add(manifest_path: Path) -> None:
        manifest_path = manifest_path.resolve()
        if manifest_path in seen:
            return
        seen.add(manifest_path)
        try:
            result.projects.append(load_project(manifest_path))
        except ManifestError as exc:
            result.errors.append((manifest_path, str(exc)))

    # 工作区根目录本身就是项目根目录的情况
    root_manifest = root / "ops" / "project.toml"
    if root_manifest.is_file():
        add(root_manifest)

    # 工作区根目录就是 ops 目录的情况
    if root.name == "ops" and (root / "project.toml").is_file():
        add(root / "project.toml")

    base_depth = len(root.parts)
    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        depth = len(current_path.parts) - base_depth
        dirnames[:] = [
            name for name in dirnames
            if name not in DEFAULT_EXCLUDES and not name.startswith(".")
        ]
        if depth >= max_depth:
            dirnames[:] = []
            continue
        if current_path.name == "ops" and "project.toml" in filenames:
            add(current_path / "project.toml")

    result.projects.sort(key=lambda project: project.slug)
    return result
