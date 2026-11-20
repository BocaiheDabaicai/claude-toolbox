# nuxt-fullstack

Nuxt 4 全栈业务应用 Skill：页面、API、PostgreSQL 直连、Cookie 会话、Drizzle 迁移、统一 API 响应和 `opsctl` 运维清单。

## 前置要求

- Node.js 22.19+ / 24.11+ / 26+
- pnpm 9.15.9
- PostgreSQL

## 适用场景

- 管理后台、内部系统、MVP；
- 需要快速迭代的业务闭环；
- 希望与 `frontend-h5-project` 共用品牌色和组件风格；
- 单台 Linux 服务器上由 `python-service-ops` 统一起停。

## 快速开始

```bash
# 1. 生成项目
node .claude/skills/nuxt-fullstack/scripts/scaffold.mjs ../my-admin \
  --name my-admin \
  --title "我的管理台"

# 2. 配置数据库与管理员
cd ../my-admin
# 修改 .env：NUXT_DATABASE_URL、SEED_ADMIN_EMAIL、SEED_ADMIN_PASSWORD

# 3. 安装与初始化
pnpm install
pnpm db:generate
pnpm db:migrate
pnpm db:seed
pnpm dev

# 4. 质量门禁
pnpm check
pnpm build

# 5. 运维接入
opsctl doctor --root /srv/projects
opsctl install my-admin --root /srv/projects --apply
opsctl status my-admin --root /srv/projects
```

## 模板包含

- 登录页 + HttpOnly Cookie 会话；
- 仪表盘；
- 客户列表 / 搜索 / 分页 / 新建 / 编辑 / 软删；
- Drizzle schema + 初始迁移 + seed；
- 统一 `{ code, message, data }` 响应与 Zod 校验；
- Tailwind 4 + daisyUI 5 品牌主题；
- `ops/project.toml`、`/api/healthz`、`/api/readyz`；
- 边界检查脚本，阻止客户端引用数据库。

## 目录

```
nuxt-fullstack/
├─ SKILL.md
├─ README.md
├─ references/              # 架构、数据库、认证、UI、模式、运维、质量
├─ assets/
│  ├─ template/             # 可运行模板
│  └─ docs-templates/       # 5 份项目文档模板
└─ scripts/
   └─ scaffold.mjs          # 生成项目
```

## 版本记录

| 版本 | 日期 | 内容 |
| --- | --- | --- |
| 0.1.0 | 2026-11-20 | 初始版本：Nuxt 4.5.2 全栈模板、Drizzle 迁移、Cookie 会话、客户 CRUD、ops manifest、构建与类型检查通过 |
