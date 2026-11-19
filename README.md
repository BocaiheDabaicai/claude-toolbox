# claude-toolbox

个人 Claude Code 工具箱：集中管理可复用的 Skill，后续可扩展 MCP 配置模板。

## 目录

```
claude-toolbox/
├─ skills/
│  └─ frontend-h5-project/    # Vue3 H5 项目生成 / 旧项目迁移 Skill
└─ mcp/                       # MCP 配置模板与说明（真实密钥不入库）
```

## 已有 Skill

### frontend-h5-project

沉淀自两个真实项目：

- `fuintMemberH5`：Vue2 + uni-app 会员端迁移到 Vue3 H5（25 个页面、完整交易链路）。
- `salebate-vue3`：Vue3 + Vite 返利下单 H5（架构参考基线）。

覆盖：技术栈、目录架构、请求层与登录态、路由、Pinia、Tailwind + daisyUI UI 系统、品牌色、字体、动效、通用组件、通用函数、本地优先购物车、SKU、预订单、库存校验、迁移流程、质量门禁。

使用方式见 `skills/frontend-h5-project/README.md` 与 `SKILL.md`。

## 安装到个人 Claude Code

把 Skill 链接到 `~/.claude/skills/`，新开 Claude Code 会话即可使用。

### Windows（目录联接，推荐）

```bat
mklink /J "%USERPROFILE%\.claude\skills\frontend-h5-project" "<repo-path>\skills\frontend-h5-project"
```

例如：

```bat
mklink /J "%USERPROFILE%\.claude\skills\frontend-h5-project" "C:\Users\NfryCreator\Desktop\task_contents\claude-toolbox\skills\frontend-h5-project"
```

### macOS / Linux（软链接）

```bash
ln -s "$(pwd)/skills/frontend-h5-project" ~/.claude/skills/frontend-h5-project
```

### 不使用链接时

把 `skills/frontend-h5-project/` 复制到 `~/.claude/skills/`。以后更新需要重新复制。

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
