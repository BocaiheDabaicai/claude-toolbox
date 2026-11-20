---
name: testing-and-regression
description: 当用户要求“写测试”“测试策略”“回归清单”“上线前检查”“发布门禁”“E2E”“Vitest”“pytest”“Playwright”“接口契约测试”，或需要为前端/FastAPI/数据迁移补测试与回归流程时使用。覆盖测试分层、组件/API/契约/E2E、测试数据、回归门禁和发布检查；不覆盖性能压测、安全渗透测试和混沌工程。
version: 0.1.0
---

# 测试与回归

## 目标

用最少的测试覆盖最高风险的路径，并把“发布前必须验证什么”固化成可执行的门禁：

- 单元/组件测逻辑；
- API/契约测接口；
- E2E 只测关键链路；
- `gate.py` 统一跑构建、测试、健康检查；
- 回归报告和发布清单可审计。

## 何时使用

- 新项目需要测试策略；
- 功能开发完成，需要补单元/组件/API 测试；
- 前后端联调，需要契约测试；
- 需要 E2E 关键链路；
- 发布前需要回归门禁；
- 需要测试计划/回归报告/发布清单。

## 何时不用

- 性能压测 → k6 / Locust / JMeter；
- 安全渗透 → 专业安全测试；
- 混沌工程 → 专门平台；
- 纯样式调整，无逻辑变化。

## 测试金字塔

| 层 | 工具 | 覆盖 |
|---|---|---|
| 单元 | Vitest / pytest | 纯函数、校验、金额、日期、密码/JWT |
| 组件 | Vitest + Vue Test Utils | 表单、列表、空态、交互 |
| API | pytest + httpx | 登录、CRUD、权限、错误码、分页 |
| 契约 | OpenAPI / codegen | 字段、类型、错误结构 |
| E2E | Playwright | 登录、主链路、异常态 |
| 回归 | `gate.py` + 清单 | 构建、测试、健康检查 |

## 标准工作流

### 0. 识别关键路径

- 登录/权限/越权；
- 金额/库存/状态流转；
- 创建/更新/删除；
- 数据迁移/对账；
- 第三方回调/幂等。

### 1. 写测试计划

用 `assets/docs-templates/test-plan.md`：

- 范围/不测范围；
- 风险；
- 分层；
- 环境/测试数据；
- 关键用例；
- 入口/出口。

### 2. 单元/组件

```bash
pnpm test
```

- 纯函数/校验/金额优先；
- 组件测用户行为，不测内部实现；
- mock 网络层，不 mock 被测组件。

### 3. API/契约

```bash
uv run pytest
```

- httpx AsyncClient；
- 测试数据库；
- 401/403/400/404；
- `/openapi.json` 关键路由；
- 响应 `{ code, message, data }`。

### 4. E2E

```bash
pnpm exec playwright test
```

- 只测关键链路；
- role/testid 选择器；
- 不 sleep；
- 失败保留 trace/screenshot。

### 5. 回归门禁

```bash
python scripts/gate.py --config gate.toml --list
python scripts/gate.py --config gate.toml --dry-run
python scripts/gate.py --config gate.toml
```

`gate.toml` 支持：

- `command`：构建、测试、lint、迁移；
- `http`：healthz/readyz、关键接口；
- `file`：配置/构建产物是否存在。

### 6. 发布

按 `assets/docs-templates/release-checklist.md`：

- 功能点 `accepted`；
- 门禁全绿；
- 备份；
- 迁移；
- 部署；
- 健康检查；
- 主链路冒烟；
- 观察/回滚。

## 门禁脚本

```bash
python scripts/gate.py --config gate.toml
python scripts/gate.py --config gate.toml --only backend-tests
python scripts/gate.py --config gate.toml --fail-fast
python scripts/gate.py --config gate.toml --dry-run
python scripts/gate.py --config gate.toml --json
```

- 默认全部检查；
- 失败退出码 1；
- 报告写 `project.report`；
- `--dry-run` 不执行；
- 命令来自本地可信配置。

## 硬性规则

- 测试不连生产库/生产接口。
- 金额、权限、状态流转、迁移必须有测试。
- 测试行为，不测实现细节。
- 不用 `sleep` 等异步；用自动等待。
- 测试数据可重复、可清理、不含真实个人信息。
- E2E 只覆盖关键链路，不堆数量。
- flaky 用例要记录、隔离、修复。
- 发布前必须跑门禁；失败不发布。
- 回滚方案必须验证。

## 质量门禁

- `pnpm test` / `uv run pytest` 通过；
- 类型检查/构建通过；
- 关键 E2E 通过；
- `/openapi.json` 关键路由存在；
- `/healthz`、`/readyz` 正常；
- `gate.py` 全部通过；
- 回归报告/发布清单已填；
- 无未处理的 flaky/严重缺陷。

## 资源索引

### references

- `references/strategy.md`：测试金字塔、风险排序、环境、数据、入口/出口。
- `references/frontend.md`：Vitest、组件、H5/管理台/PC、Nuxt、Playwright。
- `references/backend.md`：pytest、httpx、测试数据库、认证、迁移。
- `references/contract.md`：OpenAPI、类型生成、契约检查、破坏性变更。
- `references/e2e.md`：关键链路、选择器、稳定性、CI。
- `references/regression.md`：gate.py、发布/热修复/回滚。
- `references/quality-metrics.md`：覆盖率、flaky、缺陷逃逸、数据卫生。

### assets

- `assets/templates/gate.toml`：门禁配置示例。
- `assets/templates/frontend/`：Vitest / Playwright 配置与示例。
- `assets/templates/backend/`：pytest + httpx 示例。
- `assets/docs-templates/`：test-plan / regression-report / release-checklist。

### scripts

- `scripts/gate.py`：回归门禁执行器。
- `scripts/scaffold.py`：生成 gate.toml 与 docs。

## 不要做的事

- 不要用 E2E 覆盖所有校验；
- 不要测试实现细节；
- 不要用 sleep 等异步；
- 不要连生产库跑测试；
- 不要为了覆盖率写无断言测试；
- 不要长期忽略 flaky；
- 不要在门禁失败时发布；
- 不要没有回滚方案就上线。
