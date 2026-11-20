# fastapi-service

FastAPI 模块化单体 Skill：async SQLAlchemy + PostgreSQL、Alembic 迁移、JWT Access-Token、统一 `{ code, message, data }` 响应、OpenAPI、健康检查和 `opsctl` 运维清单。

## 前置要求

- Python 3.11+
- uv
- PostgreSQL

## 快速开始

```bash
# 1. 生成项目
python .claude/skills/fastapi-service/scripts/scaffold.py ../my-api \
  --name my-api \
  --title "我的 API"

# 2. 配置
cd ../my-api
# 修改 .env：DATABASE_URL、SEED_ADMIN_EMAIL、SEED_ADMIN_PASSWORD

# 3. 安装、迁移、seed
uv sync
uv run alembic upgrade head
uv run python -m scripts.seed

# 4. 启动
uv run uvicorn app.main:app --reload --port 8000

# 5. 质量门禁
uv run pytest
uv run ruff check .

# 6. 运维接入
opsctl doctor --root /srv/projects
opsctl install my-api --root /srv/projects --apply
opsctl status my-api --root /srv/projects
```

## 模板包含

- 登录 + JWT Access-Token + Argon2 密码；
- 客户列表 / 搜索 / 分页 / 创建 / 更新 / 软删；
- 统一响应、`ApiError`、Pydantic 校验、全局异常处理；
- async SQLAlchemy 2 + asyncpg + Alembic 初始迁移；
- `/api/healthz`、`/api/readyz`、`/openapi.json`；
- pytest + httpx 测试；
- `ops/project.toml`，迁移 oneshot 失败阻止 API 启动。

## 目录

```
fastapi-service/
├─ SKILL.md
├─ README.md
├─ references/              # 架构、数据库、认证、契约、模式、运维、质量
├─ assets/
│  ├─ template/             # 可运行模板
│  └─ docs-templates/       # backend-contract / data-model / roadmap
└─ scripts/
   └─ scaffold.py           # 生成项目
```

## 版本记录

| 版本 | 日期 | 内容 |
| --- | --- | --- |
| 0.1.0 | 2026-11-20 | 初始版本：FastAPI 0.165 + SQLAlchemy 2.1 async + Alembic + JWT + 客户 CRUD + ops manifest；pytest/ruff/运行时冒烟通过 |
