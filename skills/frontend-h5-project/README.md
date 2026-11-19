# frontend-h5-project

一个可复用的前端 H5 项目生成 / 迁移 Skill。沉淀自两个真实项目：

- `fuintMemberH5`：Vue2 + uni-app 会员端迁移到 Vue3 H5（25 个页面、完整交易链路）。
- `salebate-vue3`：Vue3 + Vite 的返利下单 H5（架构参考基线）。

覆盖：技术栈、目录架构、请求层与登录态、路由、Pinia、Tailwind + daisyUI UI 系统、品牌色、字体、动效、通用组件、通用函数、本地优先购物车、SKU、预订单、库存校验、迁移流程、质量门禁。

## 快速使用

### 生成新项目

```bash
# 项目级：在当前项目根目录执行
node .claude/skills/frontend-h5-project/scripts/scaffold.mjs ../my-h5-app \
  --name my-h5-app \
  --title "我的 H5 应用" \
  --api https://api.example.com/

# 个人级：路径换成 ~/.claude/skills/frontend-h5-project/scripts/scaffold.mjs
```

生成后：

```bash
cd ../my-h5-app
pnpm install
pnpm dev
```

模板内置 DEV 演示登录，只用于预览页面骨架；接入真实后端后删除。

### 让 Claude 使用

在**新会话**中直接描述任务，例如：

- “新建一个 Vue3 H5 会员商城项目，参考 frontend-h5-project”
- “把 fuintUniapp 迁移成 Vue3 H5”
- “按 frontend-h5-project 的规范搭一个收银端 H5”

Claude 会根据 `SKILL.md` 的触发条件加载，并按需读取 references。

## 目录

```
frontend-h5-project/
├─ SKILL.md                 # 触发条件 + 核心流程 + 资源索引
├─ README.md                # 本文件
├─ references/              # 架构、UI、组件、模式、契约、迁移、质量、维护
├─ assets/
│  ├─ template/             # 可复制/可脚手架的工程骨架
│  └─ docs-templates/       # 四份项目文档模板
└─ scripts/
   └─ scaffold.mjs          # 一键生成项目
```

## 共享方式

1. **项目级**：就在当前 `.claude/skills/` 下，随仓库提交，团队拉代码后可用。
2. **个人级**：把整个 `frontend-h5-project/` 复制到 `~/.claude/skills/`，本机所有项目可用。
3. **插件**：把 Skill 放到插件的 `skills/frontend-h5-project/`，按 Claude Code 插件规范安装/分发。

保持目录自包含，不依赖当前项目中的其他文件。

## 扩展方式

- 新流程/规范 → 加到 `references/` 并在 `SKILL.md` 资源索引登记；
- 新模板/组件 → 加到 `assets/template/`，占位符与 `scripts/scaffold.mjs` 保持一致；
- 新确定性操作 → 加到 `scripts/`；
- 新项目经验 → 优先补充现有 reference，不要新建平行文档；
- 每次重要更新：修改 `SKILL.md` 的 `version`，并在下方记录。

详细规则见 `references/maintenance.md`。

## 版本记录

| 版本 | 日期 | 内容 |
| --- | --- | --- |
| 0.1.0 | 2026-11-19 | 初始版本：架构、UI、组件、模式、契约、迁移、质量、模板与脚手架 |
