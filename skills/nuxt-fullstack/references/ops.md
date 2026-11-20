# 运维接入

## 1. project.toml

模板自带：

```toml
[project]
slug = "my-admin"
name = "我的管理台"
type = "nuxt"
env_file = ".env"
after = ["postgresql.service"]

[project.health]
path = "/api/healthz"
timeout = 2

[[services]]
name = "migrate"
kind = "node"
command = "pnpm db:migrate"
oneshot = true
before = ["web"]

[[services]]
name = "web"
kind = "node"
command = "node .output/server/index.mjs"
port = 3000
health = "http://127.0.0.1:3000/api/healthz"
```

由 `python-service-ops` 的 `opsctl` 读取。

## 2. 健康检查

- `/api/healthz`：进程存活，200；
- `/api/readyz`：数据库可用，`select 1` 成功返回 200，否则 503；
- 健康接口不需要登录；
- 不要在 healthz 里查业务表或执行慢查询。

## 3. 构建与启动

```bash
pnpm install
pnpm build
node .output/server/index.mjs
```

- `drizzle-kit`、`dotenv`、`tsx` 放在 dependencies，服务器 `pnpm install --prod` 后仍可执行迁移和 seed；
- 类型检查需要 devDependencies（typescript、vue-tsc）；
- 生产启动只需要 `.output/` 与 Node；
- `PORT` 环境变量控制监听端口，默认 3000；
- systemd 通过 `EnvironmentFile=.env` 注入数据库地址和会话密钥。

## 4. 迁移

`opsctl` 生成：

```ini
[Service]
Type=oneshot
ExecStart=/bin/sh -lc 'exec pnpm db:migrate'
Restart=no
Before=my-admin-web.service
```

被依赖的 web 自动获得 `Requires=my-admin-migrate.service` 和 `After=`：

- 迁移失败 → web 不启动；
- 迁移成功 → web 正常启动；
- 迁移不要放进应用启动脚本，避免多实例重复执行。

## 5. 部署顺序

1. `pnpm install`（含 devDependencies）；
2. `pnpm db:generate` 确认无 schema diff；
3. `pnpm build`；
4. `opsctl install <slug> --root /srv/projects`；
5. review `ops/systemd/`；
6. `opsctl install <slug> --root /srv/projects --apply`；
7. `systemctl start <slug>.target`；
8. `opsctl status <slug> --root /srv/projects`；
9. 打开页面验证登录和主链路。

## 6. 权限与路径

- `ops/project.toml` 里可设置 `user` / `group`；
- 命令通过 `/bin/sh -lc` 执行，确保登录 shell 能找到 `node` / `pnpm`；
- 如果服务器使用 nvm/uv，建议在 `project.toml` 中显式设置 `environment = { PATH = "..." }` 或使用绝对路径；
- `.env` 权限 600，属主为运行用户；
- PostgreSQL 只监听内网或本地。

## 7. 回滚

- 代码回滚：保留上一个 `.output/` 或重新 checkout 构建；
- 数据库回滚：迁移默认只向前；需要回滚时写新的 down 迁移，不手改已应用版本；
- 发布前备份：`pg_dump app_<slug> > backup.sql`；
- 回滚后验证 `/api/readyz` 和登录。

## 8. 日志

- 应用日志走 stdout/stderr，systemd 收集到 journal；
- 关键错误包含请求路径、错误码，不含密码/token；
- 查看：

```bash
opsctl logs my-admin --root /srv/projects -f
journalctl -u my-admin-web.service -n 200 --no-pager
```

## 9. 上线检查

- [ ] `.env` 已配置且权限 600；
- [ ] `NUXT_SESSION_SECRET` 足够随机；
- [ ] 数据库已建、迁移已跑、seed 已完成；
- [ ] `pnpm build` 成功；
- [ ] `opsctl status` healthy；
- [ ] 登录、列表、创建、编辑、删除通过；
- [ ] 重启服务器后 target 自动拉起；
- [ ] 备份任务已配置。
