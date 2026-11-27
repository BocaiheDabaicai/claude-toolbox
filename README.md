# claude-toolbox

个人 Claude Code 工具箱：集中管理可复用的 Skill，后续可扩展 MCP 配置模板。

## 目录

```
claude-toolbox/
├─ skills/
│  ├─ data-migration/         # PostgreSQL 数据迁移、对账与切换 Skill
│  ├─ fastapi-service/        # FastAPI + PostgreSQL 模块化单体后端 Skill
│  ├─ fde-delivery/           # FDE 需求梳理、功能点台账、验收与交接 Skill
│  ├─ frontend-h5-project/    # Vue3 H5 / 管理后台 / PC 项目生成与迁移 Skill
│  ├─ nuxt-fullstack/         # Nuxt 4 + PostgreSQL 全栈业务应用 Skill
│  ├─ python-service-ops/     # 单机多项目统一启停与状态管理 Skill
│  └─ testing-and-regression/ # 测试分层、E2E、契约测试与发布门禁 Skill
└─ mcp/                       # MCP 配置模板与说明（真实密钥不入库）
```

## 已有 Skill

### frontend-h5-project

沉淀自两个真实项目：

- `fuintMemberH5`：Vue2 + uni-app 会员端迁移到 Vue3 H5（25 个页面、完整交易链路）。
- `salebate-vue3`：Vue3 + Vite 返利下单 H5（架构参考基线）。

覆盖：技术栈、目录架构、请求层与登录态、路由、Pinia、Tailwind + daisyUI UI 系统、H5/PC 品牌色、管理后台独立主题（石墨侧栏 + 冷白内容 + 深湖蓝）、字体、动效、通用组件、通用函数、H5 / 管理后台 / PC 三种布局、后台表格与表单模式、本地优先购物车、SKU、预订单、库存校验、迁移流程、质量门禁。

使用方式见 `skills/frontend-h5-project/README.md` 与 `SKILL.md`。

### nuxt-fullstack

Nuxt 4 全栈业务应用：页面、API、PostgreSQL 直连、Cookie 会话、Pinia 状态、Drizzle 迁移、统一 API 响应和 `opsctl` 运维清单。

- 适合管理后台、内部系统、MVP；
- 自带登录（Pinia 登录态）、仪表盘、客户 CRUD、Zod 校验、健康检查；
- 状态管理与 `frontend-h5-project` 一致：跨页面共享状态用 Pinia（选项式），服务端数据走 `useApiFetch`/`useAsyncData`；
- 管理台使用与 `frontend-h5-project` 相同的后台设计系统：石墨侧栏 + 冷白内容 + 深湖蓝主色；H5/PC 消费者品牌色保持不变；
- 每个项目自带 `ops/project.toml`，由 `python-service-ops` 统一启停。

使用方式见 `skills/nuxt-fullstack/README.md` 与 `SKILL.md`。

### fastapi-service

FastAPI 模块化单体后端：async SQLAlchemy + PostgreSQL、Alembic 迁移、JWT Access-Token、统一 `{ code, message, data }` 响应、OpenAPI、健康检查和 `opsctl` 运维清单。

- 适合前后端分离项目，与 `frontend-h5-project` 的请求层对齐；
- 自带登录、客户 CRUD、软删、分页、测试；
- 迁移 oneshot 失败会阻止 API 启动。

使用方式见 `skills/fastapi-service/README.md` 与 `SKILL.md`。

### fde-delivery

FDE 交付 Skill：把模糊需求变成可交付、可验收、可交接的东西。

- `brief` / `features.csv` / `glossary` / `state-machines` / `permissions` / `decisions` / `roadmap` / `delivery-log` / `acceptance` / `handoff` 十份模板；
- 垂直切片、演示、验收、交接、复盘；
- `feature_lint` 校验功能点台账；
- `scaffold` 一键生成 `docs/`。

使用方式见 `skills/fde-delivery/README.md` 与 `SKILL.md`。

### data-migration

PostgreSQL 数据迁移 Skill，覆盖完整链路：

- 源数据画像、字段映射、转换与 dry-run；
- 批量 upsert、断点续跑、幂等 key；
- 数量/金额/抽样对账；
- 切换清单与回滚方案；
- `migration-kit` 工具支持 CSV / Excel / PostgreSQL / MySQL 源。

使用方式见 `skills/data-migration/README.md` 与 `SKILL.md`。

### python-service-ops

单台 Linux 服务器上的多项目统一启动、停止、重启与运行状态管理：

- `opsctl` CLI：发现项目、生成 systemd 单元、启停、状态、日志、自检；
- 每个项目只需一份 `ops/project.toml`；
- 生产环境由 systemd 守护，`opsctl` 不常驻；
- 状态 = systemd + 健康检查 + 端口探测，支持 `--json`。

使用方式见 `skills/python-service-ops/README.md` 与 `SKILL.md`。

### testing-and-regression

测试与回归 Skill：Vitest / pytest / Playwright / 契约测试 / 发布门禁。

- 测试分层与风险排序；
- 前端单元/组件/E2E 模板；
- FastAPI pytest/httpx 模板；
- `gate.py` 统一跑构建、测试、healthz/readyz、文件检查；
- 测试计划、回归报告、发布清单。

使用方式见 `skills/testing-and-regression/README.md` 与 `SKILL.md`。

## 安装到个人 Claude Code

把 Skill 链接到 `~/.claude/skills/`，新开 Claude Code 会话即可使用。

### Windows（目录联接，推荐）

```bat
mklink /J "%USERPROFILE%\.claude\skills\frontend-h5-project" "<repo-path>\skills\frontend-h5-project"
```

例如：

```bat
mklink /J "%USERPROFILE%\.claude\skills\data-migration" "C:\Users\NfryCreator\Desktop\task_contents\claude-toolbox\skills\data-migration"
mklink /J "%USERPROFILE%\.claude\skills\fastapi-service" "C:\Users\NfryCreator\Desktop\task_contents\claude-toolbox\skills\fastapi-service"
mklink /J "%USERPROFILE%\.claude\skills\fde-delivery" "C:\Users\NfryCreator\Desktop\task_contents\claude-toolbox\skills\fde-delivery"
mklink /J "%USERPROFILE%\.claude\skills\frontend-h5-project" "C:\Users\NfryCreator\Desktop\task_contents\claude-toolbox\skills\frontend-h5-project"
mklink /J "%USERPROFILE%\.claude\skills\nuxt-fullstack" "C:\Users\NfryCreator\Desktop\task_contents\claude-toolbox\skills\nuxt-fullstack"
mklink /J "%USERPROFILE%\.claude\skills\python-service-ops" "C:\Users\NfryCreator\Desktop\task_contents\claude-toolbox\skills\python-service-ops"
mklink /J "%USERPROFILE%\.claude\skills\testing-and-regression" "C:\Users\NfryCreator\Desktop\task_contents\claude-toolbox\skills\testing-and-regression"
```

### macOS / Linux（软链接）

```bash
for skill in data-migration fastapi-service fde-delivery frontend-h5-project nuxt-fullstack python-service-ops testing-and-regression; do
  ln -s "$(pwd)/skills/$skill" ~/.claude/skills/$skill
done
```

### 不使用链接时

把需要的 `skills/<name>/` 复制到 `~/.claude/skills/`。以后更新需要重新复制。

> 新建或更新 Skill 后，需要新开 Claude Code 会话（或重新加载）才会出现在技能列表中。

## 新增 Skill

1. 在 `skills/` 下新建目录，例如 `skills/my-skill/`；
2. 至少包含 `SKILL.md`（frontmatter 有 `name` / `description` / `version`）；
3. 按需添加 `references/`、`assets/`、`scripts/`；
4. 在本 README 的「已有 Skill」中登记；
5. 链接或复制到 `~/.claude/skills/`，新开会话验证触发。

建议保持渐进式披露：`SKILL.md` 精简，细节放 references，可复制代码放 assets，确定性操作放 scripts。

## MCP 配置

`mcp/` 用于存放 MCP 的配置模板和说明。真实 token、cookie、内部地址不要提交；使用 `${ENV_VAR}` 或本地 `.env` 占位。详见 `mcp/README.md`。

## 更新

```bash
git pull
```

使用目录联接/软链接时，更新后无需重新安装；直接新开会话即可。

## 安全约定

- 不提交任何真实密钥、token、cookie、个人信息。
- `.env`、`.env.local`、`*.local`、证书文件已在 `.gitignore` 中忽略。
- 公开分享前检查 `skills/` 与 `mcp/` 中是否包含内部地址、账号或业务数据。
