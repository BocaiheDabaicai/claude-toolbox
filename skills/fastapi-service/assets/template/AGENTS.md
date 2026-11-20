# AGENTS.md

## 项目环境（硬性要求）

FastAPI 模块化单体，Python 3.11+，依赖统一用 uv 管理。

- `uv sync` 安装依赖；
- `uv run <cmd>` 执行命令；
- 不混用 pip / poetry / conda；
- `uv.lock` 提交到仓库，不手工编辑。

## 常用命令

```bash
uv sync
uv run pytest
uv run ruff check .
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "change"
uv run python -m scripts.seed
uv run uvicorn app.main:app --reload --port 8000
```

## 分层

```
router       HTTP 参数、依赖、响应
service      业务规则、错误
repository   SQLAlchemy 查询
model        表结构
schema       Pydantic 输入/输出
core         配置、安全、错误、响应、中间件
db           引擎、会话、Base、模型
```

- 路由不直接写 SQL；
- repository 不处理 HTTP；
- service 不依赖 FastAPI；
- 跨模块复用放 `app/core`。

## 硬性规则

- 全异步：使用 `AsyncSession`、`create_async_engine`，禁止同步数据库调用。
- 所有业务接口返回 `{ code, message, data }`；列表 `data: { rows, total, page, pageSize }`。
- 业务错误抛 `ApiError(code, message)`；参数错误由 Pydantic 校验并统一转为 400。
- 所有写接口必须先经过 Pydantic schema；不在路由里手写字段校验。
- 认证使用 `Access-Token` JWT；密码使用 Argon2（pwdlib）。
- CORS 只允许配置中的前端域名。
- 迁移由 Alembic 管理；已应用的迁移不改，只追加新迁移。
- 每个服务提供 `/api/healthz`、`/api/readyz`，并维护 `ops/project.toml`。
- 密钥只放 `.env`，仓库只提交 `.env.example`。

## 质量门禁

- `uv run pytest` 通过；
- `uv run ruff check .` 通过；
- `uv run alembic history` 正常；
- `/api/healthz`、`/api/readyz` 正常；
- 登录、列表、创建、更新、删除验证通过；
- OpenAPI 包含预期路由；
- `opsctl status` 显示 healthy；
- 生产环境 `ENVIRONMENT=production`、`DOCS_ENABLED=false`、真实 `JWT_SECRET`。
