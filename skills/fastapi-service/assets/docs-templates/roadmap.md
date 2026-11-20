# 交付路线图

> 项目：__PROJECT_TITLE__
> 更新日期：YYYY-MM-DD

## 1. 阶段

| 阶段 | 范围 | 交付物 | 状态 |
|---|---|---|---|
| 0. 地基 | 配置、数据库、迁移、JWT、健康检查 | 可登录、可迁移 | 待做 |
| 1. 主链路 | 客户列表 / 详情 / 创建 / 更新 / 软删 | 可验收的 API 闭环 | 待做 |
| 2. 增强 | 权限、导入导出、审计、幂等 | 按需 | 暂缓 |

## 2. 下一次开工步骤

1. 
2. 
3. 

## 3. 开发日志

| 日期 | 完成 | 遗留问题 | 下一步 |
|---|---|---|---|
|  |  |  |  |

## 4. 验收清单

- [ ] `uv sync` 通过
- [ ] `uv run alembic upgrade head` 通过
- [ ] `uv run pytest` 通过
- [ ] `uv run ruff check .` 通过
- [ ] `/api/healthz`、`/api/readyz` 正常
- [ ] 登录、列表、创建、更新、删除通过
- [ ] `opsctl status` 显示 healthy
- [ ] `docs/backend-contract.md` 与实际接口一致
