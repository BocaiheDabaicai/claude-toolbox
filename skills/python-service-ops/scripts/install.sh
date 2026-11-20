#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG="$HERE/../assets/opsctl"

if command -v uv >/dev/null 2>&1; then
  uv tool install --force "$PKG"
elif command -v pipx >/dev/null 2>&1; then
  pipx install --force "$PKG"
else
  python3 -m pip install --user --upgrade "$PKG"
fi

opsctl --version
echo "已安装。下一步：opsctl doctor --root /srv/projects"
