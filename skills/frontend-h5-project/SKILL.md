---
name: frontend-h5-project
description: 当用户要求“新建前端项目”“搭建 Vue3 H5 工程”“做管理后台”“做 PC 网站”“H5 / 管理台 / PC 三端”“后台列表表单”“迁移 uni-app/Vue2 到 Vue3”“参考 salebate-vue3 或 fuintMemberH5”“生成会员端 H5”“沉淀前端项目规范”，或需要一个可复用的 Vue 3 + Vite + Tailwind + Pinia 前端项目骨架时使用。覆盖 H5 / 管理后台 / PC 三种布局、项目生成、旧项目迁移、架构设计、UI 设计系统、通用组件与函数、接口契约和质量门禁。
version: 0.2.0
---

# 前端 H5 / 管理后台 / PC 项目生成与迁移

## 目标

用一套已在真实项目验证过的 Vue 3 + Vite 架构，生成新项目或迁移旧项目，并覆盖三种界面形态：移动端 H5、管理后台、PC 站点。产出应具备：清晰的目录结构、统一的请求层与登录态、品牌化 UI、可复用组件、可交接的文档与质量门禁。

## 何时使用

- 新建 Vue 3 + Vite 的移动端 H5 项目；
- 新建管理后台，需要列表、筛选、分页、表单、弹窗等后台模式；
- 新建 PC 站点，需要顶部导航、宽内容区和响应式布局；
- 同一项目需要 H5 / 管理台 / PC 多种界面形态，并共用设计令牌；
- 把 Vue2 / uni-app / HBuilderX / uview 项目迁移到 H5；
- 要求与 `salebate-vue3`、`fuintMemberH5` 架构保持一致；
- 需要沉淀团队的前端项目规范、组件库、通用函数与迁移流程；
- 需要搭建会员商城、返利、收银等电商类 H5 骨架。

不适用：单页面小改动、纯样式/文案调整、纯后端开发；需要前后端聚合、直连数据库 → 用 `nuxt-fullstack`。

## 三种界面形态

| 形态 | 布局 | 路由组 | 典型页面 |
| --- | --- | --- | --- |
| H5 会员端 | `DefaultLayout` + 底部导航 | `/` | 商城、返利、收银、订单 |
| 管理后台 | `AdminLayout`（侧边栏 + 顶栏 + `max-w-7xl`） | `/admin` | 仪表盘、列表、表单、导入导出 |
| PC 站点 | `PcLayout`（顶部导航 + 宽内容区） | `/site` | 官网、内容页、宽屏业务 |

三种形态共用 `colors.css`、字体、动效和基础交互；布局、导航和密度按形态调整，不维护第二套主题。

## 两种模式

### A. 新项目生成

1. 确认项目名、标题、目标目录、接口 Base URL、品牌色是否沿用；
2. 用脚手架生成骨架；
3. 按目标后端实现请求层、登录态、路由守卫；
4. 按页面清单逐页实现。

### B. 旧项目迁移

1. 盘点旧项目路由，区分「在用 / 条件可达 / 排除」；
2. 调研后端契约，产出四份文档；
3. 生成骨架；
4. 先做基础设施，再按依赖顺序迁移页面；
5. 每阶段构建、测试、更新路线图。

## 标准工作流

### 0. 确认输入

开始前必须明确：

- 旧项目路径 / 目标项目路径（迁移模式）；
- 参考项目路径（默认本 Skill 的模板即可，除非用户指定）；
- 后端环境、接口前缀、证书/域名限制；
- 迁移范围：哪些页面必须做，哪些不做；
- 界面形态：只做 H5、只做管理台、只做 PC，还是多形态并存；
- 是否保留多端（本 Skill 默认做 Web：H5 / 管理台 / PC，不做小程序条件编译）；
- 品牌色与字体是否沿用。

信息不足时先问，不要猜后端字段和业务规则。

### 1. 盘点与文档（迁移模式必做）

先产出四份文档，再写代码：

- `docs/architecture.md`：技术栈、目录、请求层、登录、路由、状态、UI 约定；
- `docs/backend-contract.md`：环境、请求头、响应结构、登录流程、接口清单、已知坑；
- `docs/pages.md`：在用/条件/排除页面、路由映射、底部导航；
- `docs/roadmap.md`：阶段计划、开发日志、下一次开工步骤、验收与回归。

模板见 `assets/docs-templates/`。文档先行是硬要求，不要“边写边猜”。

### 2. 生成骨架

使用 `scripts/scaffold.mjs`（路径按 Skill 的实际位置调整；个人级为 `~/.claude/skills/frontend-h5-project/scripts/scaffold.mjs`）：

```bash
node .claude/skills/frontend-h5-project/scripts/scaffold.mjs <target-dir> \
  --name my-h5-app \
  --title "我的 H5 应用" \
  --api https://api.example.com/
```

脚本会：

- 复制 `assets/template` 到目标目录；
- 替换 `__PROJECT_NAME__`、`__PROJECT_TITLE__`、`__API_BASE__`、`__STORAGE_PREFIX__`；
- 生成 `docs/` 四份模板。

模板已包含三种布局和示例路由：

- `/`：H5 会员端；
- `/admin`：管理后台（仪表盘 + 客户管理示例）；
- `/site`：PC 站点首页。

也可以手动复制 `assets/template`，但必须自行替换上述占位符。

生成后执行：

```bash
cd <target-dir>
pnpm install
pnpm dev
pnpm build
```

### 3. 基础设施

按目标后端实现：

- `src/utils/request.js`：请求头、响应结构、登录过期、`silent`；
- `src/utils/auth.js`：token / userId 存取，key 带项目前缀；
- `src/stores/user.js`：登录、`getInfo`、退出、reset；
- `src/stores/config.js`（如后端要求）：登录前初始化 storeId / merchantNo；
- `src/router/index.js`：初始化 → 未登录 → 恢复用户 → 已登录不进登录页；
- `src/router/legacy.js`：旧路径映射（迁移模式）；
- 全局 Toast / Confirm / Skeleton / LoadMore。

验收：清空 localStorage 后登录链路可用；请求头在 Network 可见；刷新能恢复用户信息。

### 4. 分阶段页面

按依赖顺序推进：

1. 登录页；
2. 首页（banner、分类、商品列表、店铺切换）；
3. 基础购买链路（分类/微店 → 商品详情 → SKU → 购物车 → 结算 → 预订单）；
4. 订单与售后；
5. 我的、个人信息、钱包、积分；
6. 内容页（文章、消息，可选）。

每个阶段只做一组页面；先确认范围再动手。

管理后台按「登录 → 仪表盘 → 第一个 CRUD → 筛选/导入导出」推进；PC 站点按「首页 → 内容页 → 转化页」推进。三种形态共用请求层、登录态和设计令牌，不要复制三套基础设施。

### 5. 验收与交接

每阶段收尾：

```bash
pnpm build
git diff --stat pnpm-lock.yaml
```

- 构建通过，锁文件无漂移；
- 主链路、空态、错误态、加载态验证；
- 二级页返回、hash 刷新、移动端宽度检查；
- 更新 `docs/roadmap.md` 开发日志与「下一次开工步骤」；
- 询问是否提交（默认本地提交，不推送，除非用户明确要求）。

## 硬性基线

- Vue 3.5 + Vite 8 + vue-router 5（hash）+ Pinia 4（选项式）+ Tailwind CSS 4 + daisyUI 5 + axios + big.js。
- Node 20.19+ / 22.12+；pnpm 9.15.9；`.npmrc` 开启 `engine-strict=true`。
- 只用 pnpm；禁止 npm / yarn / bun；禁止删除或重建 `pnpm-lock.yaml`。
- 颜色只用语义类；新增色值登记项目的 `src/assets/styles/colors.css`。
- H5：`max-w-md` 居中、4 tab 底栏、二级页 `meta.hideBottomNav` + `meta.backTo`。
- 管理台：`AdminLayout` 侧边栏 + 顶栏 + `max-w-7xl`；列表用表格，操作区右对齐。
- PC：`PcLayout` 顶部导航 + `max-w-7xl` 宽内容区；移动端仍可用。
- 三种形态通过路由组选择布局；`meta.hideBottomNav` 隐藏 H5 底栏。
- 异步页面用骨架屏 + `swap` 过渡；图片用渐变占位 + 500ms 淡入 + 失败兜底。
- 金额用 `big.js`；富文本必须白名单清洗后再 `v-html`。
- 不做全局 loading、全局 Vuex、Vue2 mixin、HBuilderX 依赖。

## 文档先行

迁移模式没有四份文档不开工。文档不是一次性产物：

- 联调发现字段/行为不一致 → 先改 `backend-contract.md`；
- 页面范围变化 → 改 `pages.md`；
- 每个阶段 → 追加 `roadmap.md` 开发日志；
- 新会话接手 → 先读 README → architecture → backend-contract → pages → roadmap。

## 质量门禁

- `pnpm build` 通过；
- `pnpm-lock.yaml` 无非预期改动；
- 真实后端或 mock 验证通过；
- 320 / 375 / 414 宽度正常；
- 浏览器返回、刷新、hash 直开正常；
- 控制台无 error / warning；
- 文档与进度已更新；
- 用户确认界面效果（界面类改动）。

## 资源索引

### references（按需加载）

- `references/architecture.md`：技术栈、目录、启动顺序、请求层、登录态、路由、状态、反模式。
- `references/ui-system.md`：品牌色、语义色、字体、布局、动效、图片加载、空/错/加载态。
- `references/admin-and-pc.md`：管理后台 / PC 布局、路由组、表格与表单模式、响应式检查。
- `references/components.md`：通用组件清单、props/events、动态返回、分页、日期选择、业务组件模式。
- `references/patterns.md`：本地优先购物车、结算模式、再下一单与库存、登录前初始化、旧路径映射、富文本清洗、金额/日期、分页竞态。
- `references/backend-contract.md`：契约调研顺序、fuint/RuoYi 响应形态、登录流程、分页归一化、已知坑记录。
- `references/migration-playbook.md`：盘点、文档、阶段顺序、uni-app → Web 对照、范围纪律、交接。
- `references/quality-and-workflow.md`：环境/构建门禁、测试策略、回归清单、完成定义、提交约定。
- `references/maintenance.md`：Skill 的共享方式与扩展方法。

### assets

- `assets/template/`：可直接复制/脚手架的工程骨架（Vue 3 + Vite + Tailwind + Pinia + 通用组件 + utils + 路由 + 登录页占位）。
- `assets/docs-templates/`：architecture / backend-contract / pages / roadmap 四份文档模板。

### scripts

- `scripts/scaffold.mjs`：生成项目骨架，替换占位符并生成 docs。

## 扩展 Skill

新增知识时：

1. 流程/规范 → `references/`；
2. 可复制代码/模板 → `assets/`；
3. 确定性操作 → `scripts/`；
4. 在本文「资源索引」中登记；
5. 更新 `version` 与 README 版本记录；
6. 跑一次脚手架与模板构建自检。

详细规则见 `references/maintenance.md`。

## 不要做的事

- 没有后端契约就开始写页面；
- 迁移置灰、注释、无入口的页面；
- 为了“能装上”改用 npm/yarn 或删除锁文件；
- 在页面里重复拼请求头、判断错误码、弹全局提示；
- 直接 `v-html` 后端富文本；
- 用浮点数算金额；
- 把 mock、demo 登录、调试按钮带进生产构建；
- 把 H5 的 `max-w-md`、底部导航和移动端密度硬套到管理台或 PC；
- 为管理台 / PC 新建第二套颜色、字体或基础组件；
- 管理台里直接堆裸表格和裸表单，不复用分页、Toast、Confirm。
