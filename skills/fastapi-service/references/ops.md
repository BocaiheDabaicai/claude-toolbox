# 运维接入

## 1. project.toml

```toml
[project]
slug = "my-api"
name = "我的 API"
type = "custom"
env_file = ".env"
after = ["postgresql.service"]

[project.health]
path = "/api/healthz"
timeout = 2

[[services]]
name = "migrate"
kind = "python"
command = "uv run alembic upgrade head"
oneshot = true
before = ["api"]

[[services]]
name = "api"
kind = "python"
command = "uv run uvicorn app.main:app --host 127.0.0.1 --port 8000"
port = 8000
health = "http://127.0.0.1:8000/api/healthz"
```

## 2. 健康检查

- `/api/healthz`：进程存活，不查数据库；
- `/api/readyz`：`SELECT 1`，成功 200，失败 503；
- 健康接口不需要登录；
- `opsctl` 默认用 `/api/healthz` 判断存活，数据库问题看 `/api/readyz`。

## 3. 启动

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- `uv run` 会根据 `pyproject.toml` 使用项目环境；
- systemd 通过 `EnvironmentFile=.env` 注入配置；
- `uv` 必须在服务用户的登录 shell PATH 中，或在 manifest 里写绝对路径；
- 生产建议 `--workers 1` 先跑通；需要多 worker 时注意内存与数据库连接数。

## 4. 迁移

`opsctl` 生成的 oneshot：

```ini
Type=oneshot
ExecStart=/bin/sh -lc 'exec uv run alembic upgrade head'
Before=my-api-api.service
```

被依赖的 API 自动获得 `Requires=` + `After=`：

- 迁移失败 → API 不启动；
- 迁移成功 → API 正常启动；
- 不在应用启动时自动迁移。

## 5. 部署顺序

1. `uv sync`；
2. `uv run pytest` / `uv run ruff check .`；
3. `uv run alembic upgrade head`（或由 oneshot 执行）；
4. `opsctl install my-api --root /srv/projects`；
5. review `ops/systemd/`；
6. `opsctl install my-api --root /srv/projects --apply`；
7. `systemctl start my-api.target`；
8. `opsctl status my-api --root /srv/projects`；
9. 调登录与主链路。

## 6. 回滚

- 代码：保留上一个版本或重新 checkout 构建；
- 数据库：迁移默认只向前；需要回滚时写新的 down 迁移，不手改历史；
- 发布前备份：`pg_dump app_<slug> > backup.sql`；
- 回滚后验证 `/api/readyz`、登录和主链路。

## 7. 日志

- 应用 stdout/stderr → journal；
- request_id 贯穿单次请求；
- 查看：

```bash
opsctl logs my-api --root /srv/projects -f
journalctl -u my-api-api.service -n 200 --no-pager
```

## 8. 生产配置

```env
ENVIRONMENT=production
DOCS_ENABLED=false
JWT_SECRET=<真实随机值>
CORS_ORIGINS=https://your-frontend.example.com
```

- `.env` 权限 600；
- PostgreSQL 只监听内网/本地；
- 数据库账号最小权限；
- 首次 seed 后修改管理员密码。

## 9. 上线检查

- [ ] `uv sync` / `uv run pytest` / `uv run ruff check .` 通过；
- [ ] `alembic upgrade head` 通过；
- [ ] `/api/healthz` 200，`/api/readyz` 200；
- [ ] 登录、列表、创建、更新、删除通过；
- [ ] `opsctl status` healthy；
- [ ] 重启服务器后 target 自动拉起；
- [ ] 备份任务已配置；
- [ ] 生产关闭 `/docs`，替换 JWT secret，CORS 收窄。
