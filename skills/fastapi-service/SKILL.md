---
name: fastapi-service
description: 当用户要求“新建 FastAPI 服务”“Python 后端”“Vue H5 + FastAPI”“SQLAlchemy async”“Alembic 迁移”“统一响应结构”“JWT Access-Token”，或需要一个可复用的 FastAPI 模块化单体骨架时使用。覆盖配置、异步数据库、认证、错误处理、分页、OpenAPI、健康检查、opsctl 运维清单和质量门禁；不覆盖微服务/服务网格、消息队列、复杂工作流引擎。
version: 0.1.0
---

# FastAPI 服务

## 目标

用一套经过测试验证的 FastAPI 模块化单体架构，快速生成前后端分离项目的后端服务，并与现有 Vue H5 / 管理台前端契约对齐。

## 何时使用

- 新建 FastAPI 服务，连接 PostgreSQL；
- Vue H5 / 管理台需要独立后端；
- 需要 async SQLAlchemy + Alembic 迁移；
- 需要 JWT 认证、统一响应、分页、错误处理；
- 需要 OpenAPI、健康检查和 `opsctl` 统一运维。

## 何时不用

- 只需要页面 + API 一体、快速成形 → 用 `nuxt-fullstack`；
- 纯移动端 H5 前端 → 用 `frontend-h5-project`；
- 微服务、服务网格、消息队列 → 需要单独架构；
- 复杂工作流、规则引擎、强事务金融核心 → 需要专项评估。

## 技术基线

| 类别 | 选型 | 版本 |
|---|---|---|
| 语言 | Python | 3.11+ |
| 框架 | FastAPI | 0.165.x |
| ASGI | Uvicorn | 0.54.x |
| ORM | SQLAlchemy（async） | 2.1.x |
| 驱动 | asyncpg | 0.32.x |
| 迁移 | Alembic | 1.20.x |
| 校验 | Pydantic / pydantic-settings | 2.14.x / 2.16.x |
| 认证 | PyJWT + pwdlib[argon2] | 2.15.x / 0.4.x |
| 工具 | uv / ruff / pytest | 当前稳定版 |

## 架构

```
app/
├─ main.py              # FastAPI 实例、CORS、中间件、异常处理
├─ api.py               # /api 路由聚合
├─ core/                # 配置、JWT、密码、错误、响应、请求日志
├─ db/                  # Base、模型、异步会话
└─ modules/
   ├─ auth/             # 登录、当前用户、依赖
   ├─ customers/        # 业务模块：schemas / repository / service / router
   └─ health/           # healthz / readyz
migrations/             # Alembic
scripts/seed.py         # 管理员 + 示例数据
tests/                  # pytest + httpx
ops/project.toml        # opsctl 清单
```

分层：

```
router → service → repository → model
   ↓         ↓
 schema   ApiError
```

- router 只处理 HTTP 参数、依赖和响应；
- service 负责业务规则与错误；
- repository 负责 SQLAlchemy 查询；
- 全异步，禁止同步数据库调用。

## 接口契约

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

认证：

- 登录：`POST /api/auth/login`；
- 请求头：`Access-Token: <token>`（兼容 `Authorization: Bearer <token>`）；
- 401 时前端清 token 回登录页。

## 标准工作流

### 0. 确认输入

- 项目 slug、数据库名（建议 `app_<slug>`）；
- 前端地址（CORS）；
- 管理员邮箱与初始密码；
- 服务端口（默认 8000）。

### 1. 生成项目

```bash
python .claude/skills/fastapi-service/scripts/scaffold.py ../my-api \
  --name my-api \
  --title "我的 API"
```

脚本会复制模板、替换占位符、生成 `docs/` 和带随机 `JWT_SECRET` 的 `.env`。

### 2. 文档与数据库

```bash
cd ../my-api
# 修改 .env：DATABASE_URL、SEED_ADMIN_*
uv sync
uv run alembic upgrade head
uv run python -m scripts.seed
uv run uvicorn app.main:app --reload --port 8000
```

### 3. 验证

```bash
curl http://127.0.0.1:8000/api/healthz
curl http://127.0.0.1:8000/api/readyz
uv run pytest
uv run ruff check .
```

### 4. 按业务模块开发

每个业务域：

1. `app/db/models.py` 加表；
2. `uv run alembic revision --autogenerate -m "add xxx"`；
3. `app/modules/<domain>/schemas.py`；
4. `repository.py`；
5. `service.py`；
6. `router.py`；
7. `app/api.py` 挂载；
8. 补测试与文档。

### 5. 运维接入

确认 `ops/project.toml` 后：

```bash
opsctl doctor --root /srv/projects
opsctl install my-api --root /srv/projects
opsctl install my-api --root /srv/projects --apply
opsctl status my-api --root /srv/projects
```

## 硬性规则

- 全异步：`AsyncSession` + `create_async_engine`，禁止同步数据库调用。
- 所有业务接口返回 `{ code, message, data }`；列表 `data: { rows, total, page, pageSize }`。
- 业务错误抛 `ApiError(code, message)`；参数错误由 Pydantic 统一转 400。
- 路由不直接写 SQL；repository 不处理 HTTP。
- 认证使用 JWT `Access-Token`；密码使用 Argon2。
- CORS 只允许 `CORS_ORIGINS` 中的前端地址。
- 迁移由 Alembic 管理；已应用迁移不改，只追加。
- 密钥只放 `.env`；生产环境必须替换默认 `JWT_SECRET`。
- 每个服务提供 `/api/healthz`、`/api/readyz` 和 `ops/project.toml`。

## 质量门禁

- `uv run pytest` 通过；
- `uv run ruff check .` 通过；
- `uv run alembic history` 正常；
- `/api/healthz` 200，`/api/readyz` 数据库可用时 200；
- `/openapi.json` 包含预期路由；
- 登录、列表、创建、更新、删除主链路通过；
- `opsctl status` 显示 healthy；
- 文档与 `backend-contract.md` 一致。

## 资源索引

### references（按需加载）

- `references/architecture.md`：分层、请求流、响应封装、异常处理、配置、CORS、OpenAPI。
- `references/database.md`：async SQLAlchemy、模型、会话、分页、软删、Alembic、事务。
- `references/auth.md`：JWT Access-Token、Argon2、依赖注入、安全清单。
- `references/api-contract.md`：响应结构、分页、错误码、接口清单、前端对接。
- `references/patterns.md`：CRUD、搜索分页、软删、校验、幂等、seed、加模块流程。
- `references/ops.md`：project.toml、迁移 oneshot、uvicorn、systemd、部署与回滚。
- `references/quality.md`：命令、测试、回归、安全、性能、版本说明。

### assets

- `assets/template/`：可运行的 FastAPI 模板（登录、客户 CRUD、迁移、测试、ops manifest）。
- `assets/docs-templates/`：backend-contract / data-model / roadmap。

### scripts

- `scripts/scaffold.py`：复制模板、替换占位符、生成 docs 与 `.env`。

## 与其他 Skill 的关系

- `frontend-h5-project`：H5 / 管理台 / PC 前端；本服务对齐其请求层与响应结构。
- `nuxt-fullstack`：前后端聚合项目，不需要本服务。
- `python-service-ops`：读取 `ops/project.toml`，统一启停与状态。

## 不要做的事

- 不要在路由里直接写 SQL 或同步数据库调用；
- 不要返回裸数组或 `{ data }` 之外的业务结构；
- 不要把密码、JWT、数据库地址写进代码；
- 不要手改已应用的迁移；
- 不要为每个模块复制一套异常处理；
- 不要在生产环境开启默认 JWT secret、宽 CORS 或 `/docs`；
- 不要把 FastAPI 服务拆成微服务，除非有明确边界和运维能力。
