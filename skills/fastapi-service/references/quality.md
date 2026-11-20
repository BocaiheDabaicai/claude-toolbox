# 质量与验收

## 1. 命令

```bash
uv sync
uv run pytest
uv run ruff check .
uv run alembic history
uv run alembic upgrade head
```

## 2. 合并前门禁

- `uv run pytest` 通过；
- `uv run ruff check .` 通过；
- `uv run alembic history` 正常；
- 新增/修改模型已生成迁移；
- 新增接口有 Pydantic schema 和错误处理；
- 没有 `print` 调试输出（seed/脚本除外）；
- `uv.lock` 已更新并提交；
- 文档与接口一致。

## 3. 测试策略

当前模板包含：

- healthz / readyz；
- 参数校验错误信封；
- 未登录 401；
- 密码 hash/verify；
- JWT 签发/解码/无效 token；
- OpenAPI 路由存在。

后续补：

- 使用独立测试 database，跑迁移 + seed；
- 登录 → 列表 → 创建 → 更新 → 软删集成测试；
- 事务回滚测试；
- 并发/幂等测试；
- 第三方集成 mock。

## 4. 回归清单

- [ ] 登录成功返回 token + user；
- [ ] 错误密码返回 401，不泄露账号是否存在；
- [ ] 无 token 访问受保护接口返回 401；
- [ ] token 过期返回 401；
- [ ] 列表搜索/分页/软删过滤；
- [ ] 创建：必填/长度/邮箱校验；
- [ ] 更新：不存在返回 404；
- [ ] 删除：软删后列表不可见；
- [ ] `/api/healthz`、`/api/readyz`；
- [ ] `/openapi.json` 路由完整。

## 5. 安全

- 客户端代码/日志不含数据库地址、JWT secret、密码 hash；
- 生产替换默认 `JWT_SECRET`；
- 生产 `DOCS_ENABLED=false`；
- CORS 只允许实际域名；
- 错误响应不含堆栈；
- 登录错误统一文案；
- 数据库账号最小权限；
- `.env` 权限 600；
- 后续加登录限流、refresh token、密钥轮换。

## 6. 性能

- 列表只查需要字段（数据量大时用 `select(Model.id, Model.name, ...)`）；
- 分页有上限；
- 搜索字段有索引；
- 避免 N+1；
- 大字段不在列表全量返回；
- 用 `EXPLAIN ANALYZE` 验证慢查询；
- 连接池大小与 worker 数匹配。

## 7. 版本说明

- FastAPI 0.165.x；
- SQLAlchemy 2.1.x（async）；
- Alembic 1.20.x；
- Pydantic 2.14.x；
- asyncpg 0.32.x；
- PyJWT 2.15.x；
- pwdlib 0.4.x（Argon2）；
- Python 3.11+。

升级时先跑 `uv sync`、`uv run pytest`、`uv run ruff check .`、`uv run alembic history`，确认没有行为变化。
