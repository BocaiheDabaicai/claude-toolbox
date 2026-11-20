# __PROJECT_TITLE__

FastAPI 模块化单体模板：async SQLAlchemy + PostgreSQL、Alembic 迁移、JWT Access-Token、统一 `{ code, message, data }` 响应。

> 本模板通过 `fastapi-service/scripts/scaffold.py` 生成；不要直接对未替换占位符的模板执行 `uv sync`（`pyproject.toml` 的 name 还不是合法包名）。

## 前置要求

- Python 3.11+
- uv
- PostgreSQL

## 快速开始

```bash
cp .env.example .env
# 修改 DATABASE_URL、JWT_SECRET、SEED_ADMIN_*

uv sync
uv run alembic upgrade head
uv run python -m scripts.seed
uv run uvicorn app.main:app --reload --port 8000
```

- 健康检查：`GET /api/healthz`、`GET /api/readyz`
- 接口文档：`GET /docs`、`GET /openapi.json`
- 登录：`POST /api/auth/login`，返回 `data.token`
- 后续请求带 `Access-Token: <token>` 或 `Authorization: Bearer <token>`

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

## 目录

```
app/
├─ main.py              # FastAPI 实例、CORS、异常处理、路由挂载
├─ api.py               # /api 路由聚合
├─ core/                # 配置、JWT、密码、错误、响应、中间件
├─ db/                  # Base、模型、异步会话
└─ modules/
   ├─ auth/             # 登录、当前用户、依赖
   ├─ customers/        # 客户 CRUD
   └─ health/           # healthz / readyz
migrations/             # Alembic
scripts/seed.py         # 管理员 + 示例客户
tests/                  # pytest + httpx
ops/project.toml        # opsctl 清单
```

## 响应约定

成功：

```json
{ "code": 200, "message": "ok", "data": {} }
```

列表：

```json
{ "code": 200, "message": "ok", "data": { "rows": [], "total": 0, "page": 1, "pageSize": 20 } }
```

错误：

```json
{ "code": 400, "message": "请求参数不合法", "data": null, "details": [] }
```

## 部署

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

由 `python-service-ops` 的 `opsctl` 统一管理；`ops/project.toml` 已声明迁移 oneshot 和健康检查。

## 安全

- `.env` 不入库，服务器上 `chmod 600`；
- `JWT_SECRET` 至少 32 位随机字符；生产环境必须替换默认值；
- 生产环境建议 `DOCS_ENABLED=false`、`ENVIRONMENT=production`；
- CORS 只允许实际前端域名；
- 首次登录后尽快修改 seed 管理员密码。
