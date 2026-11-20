# systemd 生成与控制

## 生成结构

一个项目生成：

```
<project>/ops/systemd/
├─ crm-web.service
├─ crm-migrate.service
└─ crm.target
```

- 每个 `[[services]]` 一个 `.service`；
- 一个项目一个 `<slug>.target`，把服务聚合起来；
- 服务通过 `PartOf=<slug>.target` 挂到 target。

## 服务单元示例

```ini
[Unit]
Description=CRM - web
Wants=network-online.target
After=network-online.target postgresql.service
PartOf=crm.target

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/srv/projects/crm
EnvironmentFile=-/srv/projects/crm/.env.production
Environment=NODE_ENV=production
ExecStart=/bin/sh -lc 'exec node .output/server/index.mjs'
Restart=on-failure
RestartSec=3
TimeoutStopSec=15
KillSignal=SIGTERM
StandardOutput=journal
StandardError=journal
SyslogIdentifier=crm-web
```

## target 示例

```ini
[Unit]
Description=CRM
Wants=network-online.target crm-migrate.service crm-web.service
After=network-online.target crm-migrate.service crm-web.service

[Install]
WantedBy=multi-user.target
```

## 为什么用 target + PartOf

- `systemctl start crm.target` 一次拉起项目内所有服务；
- `systemctl stop crm.target` 通过 `PartOf` 传播停止；
- `systemctl restart crm.target` 通过 `PartOf` 传播重启；
- 只 enable target 就能开机自启，不需要逐个 enable 服务；
- 单个服务仍可单独 `systemctl restart crm-web.service`。

## 一次性任务（迁移）

```toml
[[services]]
name = "migrate"
command = "pnpm db:migrate"
oneshot = true
before = ["web"]
```

生成：

```ini
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/sh -lc 'exec pnpm db:migrate'
Restart=no
```

`Before=crm-web.service` 保证迁移先执行；同时 `web` 单元会得到：

```ini
Requires=crm-migrate.service
After=crm-migrate.service
```

因此迁移失败时，依赖它的 `web` 不会启动，避免带着旧表结构跑业务。

`RemainAfterExit=yes` 让 `status` 能看到迁移已完成；失败时 `ActiveState=failed`，需要人工处理。

## 命令执行与 PATH

生成的 `ExecStart` 是：

```ini
ExecStart=/bin/sh -lc 'exec <command>'
```

原因：

- systemd 不读 `.bashrc`，直接写 `node` / `uv` 可能找不到；
- 登录 shell 会加载 `/etc/profile`、`~/.profile`，nvm、uv、pnpm 的 PATH 通常在这里配置；
- 仍建议在 `doctor` 里确认命令可见。

如果服务器没有为服务用户配置登录 shell PATH，用绝对路径：

```toml
command = "/usr/local/bin/node .output/server/index.mjs"
```

或显式传 PATH：

```toml
environment = { PATH = "/usr/local/bin:/usr/bin:/bin" }
```

## 环境变量

优先用 `EnvironmentFile`：

```toml
env_file = ".env.production"
```

- 生成 `EnvironmentFile=-<absolute path>`；
- 前面的 `-` 表示文件不存在时不报错；
- 文件建议 `chmod 600`，属主为运行用户；
- 不要把密钥写进 manifest 的 `environment`。

## 安装与启用

```bash
# 只生成到项目内，便于 review
opsctl install crm --root /srv/projects

# 安装到系统并 enable（非 root 时内部调用 sudo）
opsctl install --root /srv/projects --apply
```

如果 sudo 重置 PATH 导致找不到 `opsctl`：

```bash
sudo "$(command -v opsctl)" install --root /srv/projects --apply
```

`--apply` 会：

1. `install -m 0644` 复制单元到 `/etc/systemd/system/`；
2. `systemctl daemon-reload`；
3. `systemctl enable <slug>.target`。

不会自动 start。需要时显式执行：

```bash
sudo systemctl start crm.target
```

## 权限

- 系统级单元需要 root 或 sudo；
- `opsctl` 在非 root 时会尝试 `sudo`；
- 自动化场景建议给部署用户配置最小 sudoers，只允许操作本项目的 target 和服务；
- 用户级 systemd（`systemctl --user`）不在当前 scope。

## 日志

```bash
opsctl logs crm --root /srv/projects
opsctl logs crm --root /srv/projects --service web -f
```

底层是 `journalctl -u crm-web.service -u crm-api.service ...`。

常用排查：

```bash
systemctl status crm.target
systemctl cat crm-web.service
journalctl -u crm-web.service -n 200 --no-pager
```

## 常见 systemd 退出码

| 退出码 | 含义 | 处理 |
|---|---|---|
| `203/EXEC` | 命令找不到或不可执行 | 用绝对路径，或修正 PATH |
| `200/CHDIR` | 工作目录不存在 | 检查 `working_dir` / `root` |
| `217/USER` | User/Group 不存在 | 检查 `user` / `group` |
| `1` | 应用自身启动失败 | 看应用日志与环境变量 |

## 重启策略

- `Restart=on-failure`：默认，进程非 0 退出或崩溃时重启；
- `Restart=always`：总是重启；谨慎用于会正常退出的任务；
- `Restart=no`：不重启；用于 `oneshot` 迁移；
- `RestartSec` 控制间隔，默认 3 秒。
