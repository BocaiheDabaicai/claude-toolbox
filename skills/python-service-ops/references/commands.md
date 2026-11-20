# opsctl 命令参考

## 全局选项

| 选项 | 说明 |
|---|---|
| `--version` | 打印版本 |
| `--no-color` | 禁用 ANSI 颜色；放在子命令前，如 `opsctl --no-color status` |

退出码：

- `0`：成功；`status` 表示全部项目 `healthy`；
- `1`：错误，或 `status` 存在非 healthy 项目；
- `130`：用户中断。

## list

```bash
opsctl list --root /srv/projects
opsctl list --root /srv/projects --json
```

扫描 `<root>/*/ops/project.toml`（最大 4 层，跳过 `node_modules`、`.git`、`.venv` 等），列出项目、服务和单元名。

JSON 结构：

```json
[
  {
    "slug": "crm",
    "name": "CRM",
    "type": "nuxt",
    "root": "/srv/projects/crm",
    "manifest": "/srv/projects/crm/ops/project.toml",
    "services": [
      {"name": "web", "unit": "crm-web.service", "port": 3000}
    ]
  }
]
```

## status

```bash
opsctl status --root /srv/projects
opsctl status crm --root /srv/projects
opsctl status --root /srv/projects --json
```

每个服务检查：

1. systemd 单元状态（`systemctl show`）；
2. 端口是否监听；
3. HTTP 健康地址（若配置）。

项目状态：

- `healthy`：所有服务 systemd active + 端口正常 + 健康检查通过；
- `degraded`：部分服务 active / 端口开放 / 健康通过；
- `stopped`：没有任何服务在运行；
- `empty`：没有服务（manifest 不应出现）。

`status` 对非 healthy 返回退出码 1，可直接用于监控脚本。

JSON 结构（节选）：

```json
[
  {
    "project": "crm",
    "state": "healthy",
    "services": [
      {
        "name": "web",
        "unit": "crm-web.service",
        "port": 3000,
        "port_open": true,
        "systemd": {
          "available": true,
          "active_state": "active",
          "sub_state": "running",
          "pid": 1234,
          "restarts": 0
        },
        "health": {"ok": true, "detail": "HTTP 200", "latency_ms": 12},
        "ok": true
      }
    ]
  }
]
```

## start / stop / restart

```bash
opsctl start crm --root /srv/projects
opsctl stop crm --root /srv/projects
opsctl restart crm --root /srv/projects
opsctl restart crm --root /srv/projects --service web
opsctl start --root /srv/projects            # 所有项目
opsctl start crm --root /srv/projects --dry-run
```

- 不带 `--service` 时操作 `<slug>.target`；
- `--dry-run` 只打印 `systemctl` 命令，不执行；
- 需要 root/sudo。

## render

```bash
opsctl render crm --root /srv/projects
```

打印所有生成的单元内容，不落盘。适合 review 和排查。

## install

```bash
opsctl install crm --root /srv/projects          # 生成到 ops/systemd/
opsctl install --root /srv/projects              # 所有项目
opsctl install --root /srv/projects --apply      # 安装并 enable
opsctl install crm --root /srv/projects --apply --dry-run
```

- 默认只生成，不碰 `/etc/systemd/system`；
- `--apply` 复制、`daemon-reload`、`enable <slug>.target`；
- 非 root 时内部调用 `sudo`；如果 sudo 重置 PATH 找不到 opsctl，用 `sudo "$(command -v opsctl)" ...`；
- 不会自动 start。

## logs

```bash
opsctl logs crm --root /srv/projects
opsctl logs crm --root /srv/projects --service web -n 200
opsctl logs crm --root /srv/projects -f
```

- 不带 `--service` 时聚合项目内所有服务的 journal；
- `-f` 持续跟踪；
- `-n` 显示行数，默认 100。

## doctor

```bash
opsctl doctor --root /srv/projects
```

检查：

- Python 版本（>= 3.11）；
- 是否 Linux、是否有 systemd / journalctl；
- 当前权限与 sudo；
- manifest 是否能解析；
- 项目根目录、工作目录、env 文件；
- 启动命令第一个词是否在 PATH。

输出 `OK` / `WARN` / `ERROR`；存在 `ERROR` 时退出码 1。
