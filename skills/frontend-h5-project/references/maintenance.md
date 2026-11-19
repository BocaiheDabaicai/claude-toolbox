# Skill 使用、共享与扩展

## 1. 这个 Skill 的组成

```
frontend-h5-project/
├─ SKILL.md                 # 触发条件 + 精简流程（始终加载）
├─ README.md                # 给人看的使用/共享说明
├─ references/              # 按需加载的详细知识
│  ├─ architecture.md
│  ├─ ui-system.md
│  ├─ components.md
│  ├─ patterns.md
│  ├─ backend-contract.md
│  ├─ migration-playbook.md
│  ├─ quality-and-workflow.md
│  └─ maintenance.md
├─ assets/
│  ├─ template/             # 可复制/可脚手架的工程骨架
│  └─ docs-templates/       # 架构/契约/页面/路线图模板
└─ scripts/
   └─ scaffold.mjs          # 一键生成项目骨架
```

采用渐进式披露：SKILL.md 只保留触发条件、核心流程与资源索引；细节放 references；模板放 assets，不占用上下文。

## 2. 如何使用

### 2.1 项目级（当前位置）

本 Skill 位于当前项目的 `.claude/skills/frontend-h5-project/`。在**新会话**中，Claude Code 会加载其名称与描述；当任务匹配描述中的触发词时自动使用，也可明确要求“使用 frontend-h5-project Skill”。

> 新建/修改 Skill 后需要新开会话或重新加载，当前会话不会自动出现在技能列表。

### 2.2 个人级（跨项目）

把整个 `frontend-h5-project/` 目录复制到：

```
~/.claude/skills/frontend-h5-project/
```

个人级 Skill 在本机所有项目可用。适合自己长期使用；团队成员需要各自复制。

### 2.3 团队共享 / 插件化

三种常见方式：

1. **随仓库提交**：把 Skill 放在仓库的 `.claude/skills/`，团队拉代码后在该仓库内使用。
2. **独立仓库**：把 `frontend-h5-project/` 作为独立仓库维护，团队成员复制到个人级目录。
3. **升级为插件**：在插件根目录创建 `.claude-plugin/plugin.json`，把 Skill 放到插件的 `skills/frontend-h5-project/`，按 Claude Code 插件规范安装/分发。插件命令与市场配置以官方文档为准。

无论哪种方式，保持目录自包含：不依赖当前项目里的其他文件。

## 3. 如何扩展

### 3.1 新增一条知识

1. 判断类型：
   - 详细流程/规范 → `references/`
   - 可复制代码/模板 → `assets/`
   - 可重复执行的确定性操作 → `scripts/`
2. 在 `SKILL.md` 的「资源索引」中加一行指针；
3. 避免与现有文件重复；同一内容只放在一个地方；
4. 更新 `README.md` 的文件地图（如有必要）。

### 3.2 新增一个模板文件

- 放入 `assets/template/` 对应目录；
- 如含项目名/标题/接口地址/存储前缀，使用占位符：
  - `__PROJECT_NAME__`
  - `__PROJECT_TITLE__`
  - `__API_BASE__`
  - `__STORAGE_PREFIX__`
- 同步更新 `scripts/scaffold.mjs` 的替换表（如有新增占位符）；
- 跑一次脚手架生成到临时目录，确认文件被正确替换。

### 3.3 新增一个模式

当真实项目验证了一个新做法：

1. 在 `references/patterns.md` 增加「场景 → 做法 → 坑」；
2. 如果包含完整组件，考虑放进 `assets/template/src/components/`；
3. 如果是迁移经验，补到 `migration-playbook.md`；
4. 如果是质量/协作约定，补到 `quality-and-workflow.md`；
5. 在 `SKILL.md` 资源索引里确认可发现。

### 3.4 版本与变更

- `SKILL.md` frontmatter 维护 `version`；
- 重要变更记录在 `README.md` 的「版本记录」；
- 大改后自测：触发词、文件引用、脚手架生成、模板构建。

## 4. 自检清单

- [ ] `SKILL.md` frontmatter 有 `name` / `description` / `version`；
- [ ] description 用第三人称，包含具体触发短语；
- [ ] SKILL.md 保持精简（约 1,500–2,000 英文词/等价中文），细节在 references；
- [ ] SKILL.md 引用的文件都存在；
- [ ] 模板占位符与脚手架替换表一致；
- [ ] 脚手架生成到空目录后结构正确；
- [ ] 模板执行 `pnpm build` 通过（在接入真实后端前，DEV 演示登录可预览骨架）；
- [ ] 没有重复内容散落在多个文件；
- [ ] 共享方式说明与实际目录结构一致。

## 5. 从新项目回灌知识

每完成一个新项目/迁移，至少回灌：

- 新的后端契约形态与坑；
- 新组件/模式；
- 新的质量门禁或测试场景；
- 被证明不可行的做法（写进“不要做的事”）。

回灌时优先修改现有 references，而不是新增平行文档；保持 Skill 精炼、可发现、可维护。
