# AGENTS.md

## 项目环境（硬性要求）

本项目是 Vue 3 + Vite 8 的 H5 前端，依赖必须使用 pnpm 9 安装。

- Node.js：20.19+ 或 22.12+
- pnpm：9.x，锁定 9.15.9（见 `package.json` 的 `packageManager`）
- 安装依赖只在项目根目录执行 `pnpm install`
- 禁止使用 `npm install` / `yarn` / `bun install`，它们会生成第二套锁文件并导致依赖版本漂移
- 禁止删除、重建或手工编辑 `pnpm-lock.yaml`
- 只有任务明确要求升级依赖时，才允许更新锁文件；否则保持锁文件不变
- 不要用 `--ignore-scripts` 绕过仓库自带的 `preinstall` 环境校验

## 常用命令

```bash
pnpm install
pnpm dev
pnpm build
```

没有 pnpm 或版本不是 9.x：

```bash
corepack enable
corepack prepare pnpm@9.15.9 --activate
# 或
npm i -g pnpm@9.15.9
# 不全局安装 pnpm 时
npx pnpm@9.15.9 install
```

## 安装报错处理

- `ERR_PNPM_UNSUPPORTED_ENGINE` / `Your pnpm version is incompatible`：pnpm 版本不对，安装 9.15.9 后重试。
- `pnpm-lock.yaml` 首行变成 `lockfileVersion: '6.0'`，或 `git diff` 显示大量依赖被降级：旧版 pnpm 重写了锁文件。执行 `git checkout -- pnpm-lock.yaml`，再用 pnpm 9 重新安装；确认 `git diff pnpm-lock.yaml` 为空后再继续。
- `ERR_PNPM_OUTDATED_LOCKFILE`：锁文件与 `package.json` 不一致。先确认改动来源，不要直接删除锁文件；只有明确升级依赖时才用 pnpm 9 更新。
- Node 版本错误：升级到 Node 20.19+ 或 22.12+。
- 如果只有 npm 可用：执行 `npx pnpm@9.15.9 install`，不要改用 npm 安装项目。

## 给 AI 的行为约束

- 遇到 npm / yarn 安装请求时，先说明锁文件风险，然后改用上面的 pnpm 命令；不要为了“能装上”而删除锁文件或切换包管理器。
- 报告安装问题已解决前，先确认 `pnpm-lock.yaml` 没有非预期改动（`git diff --stat pnpm-lock.yaml`）。
- 不要修改 `packageManager`、`engines`、`.npmrc` 的版本约束来绕过报错，除非用户明确要求升级工具链。

## 前端约定

- 颜色只用 `src/style.css` 映射的语义类（`bg-primary`、`text-base-content/60` 等），新增色值先登记到 `src/assets/styles/colors.css`。
- 页面统一放在 `src/views`，通用组件放 `src/components`，接口函数放 `src/api`，跨页状态放 `src/stores`。
- 三种界面形态通过路由组选择布局：
  - H5：`DefaultLayout` + 底部导航，容器 `max-w-md`；
  - 管理台：`AdminLayout` + `src/views/admin`，容器 `max-w-7xl`；
  - PC：`PcLayout` + `src/views/pc`，容器 `max-w-7xl`。
- 管理台 / PC 路由组父级设置 `meta: { hideBottomNav: true }`，不要给每个子页重复设置。
- 后台页头用 `AdminPageHeader`；列表分页复用 `PaginationBar`；操作反馈用 `toast`，危险操作用 `confirm({ danger: true })`。
- 不要把 H5 的 `max-w-md`、底部导航、移动端密度硬套到管理台或 PC。
- 异步页面使用骨架屏 + `swap` 过渡，避免内容直接闪现；图片加载使用渐变占位 + 淡入 + 失败兜底。
- 富文本必须经过 `utils/sanitize.js` 白名单清洗后再 `v-html`，不要直接渲染后端 HTML。
- 金额计算使用 `big.js`，展示统一走 `utils/money.js`。
