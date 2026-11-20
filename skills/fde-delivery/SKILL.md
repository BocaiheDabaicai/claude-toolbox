---
name: fde-delivery
description: 当用户要求“梳理需求”“业务功能点记录”“功能清单”“排交付计划”“快速迭代”“FDE 交付”“项目启动/交接/验收/复盘”，或需要把模糊业务需求拆成可交付切片、功能点台账和验收标准时使用。覆盖 intake、brief、功能点台账、术语/状态机/权限、垂直切片、演示、验收、交接和知识回灌；不覆盖纯技术实现细节（由前端/后端/数据迁移 Skill 负责）。
version: 0.1.0
---

# FDE 交付

## 目标

把“业务想要什么”变成**可交付、可验收、可交接**的东西。核心不是写更多文档，而是：

- 需求有边界（含 Non-goals）；
- 功能点有台账（状态、负责人、验收标准、依赖）；
- 交付按垂直切片推进，每个切片都能演示；
- 决策和变更留痕；
- 验收和交接有清单；
- 项目结束后知识回灌到 Skill。

## 何时使用

- 新项目/新需求开始，需要快速理清范围；
- 业务方描述模糊，需要拆功能点；
- 需要排里程碑和垂直切片；
- 需要功能点台账、术语表、状态机、权限矩阵；
- 需要验收、交接、复盘；
- 多人协作，需要统一的文档契约。

## 何时不用

- 纯技术重构、无业务范围变化；
- 单页面小改动，不需要完整台账；
- 只需要写代码，需求和验收已完全明确；
- 具体技术实现 → 用 `frontend-h5-project`、`nuxt-fullstack`、`fastapi-service`、`data-migration`、`python-service-ops`。

## 核心原则

1. **垂直切片优先**：每个切片从页面/接口到数据都能跑通，能演示。
2. **文档即契约**：brief、features、decisions、roadmap 是协作接口，不是事后总结。
3. **功能点台账是唯一事实源**：状态、负责人、验收标准以 `features.csv` 为准。
4. **Non-goals 必须写**：明确不做什么，防止范围悄悄膨胀。
5. **决策留痕**：重要选择写 `decisions.md`，包括代价和复核条件。
6. **验收先于完成**：没有验收证据不算完成。
7. **变更有成本**：范围变更要更新台账、路线图和决策记录。

## 标准工作流

### 0. Intake

确认：

- 为什么现在做、谁用、现在怎么做；
- 成功指标；
- 范围与 Non-goals；
- 数据、系统、集成、合规约束；
- 截止时间、验收人、决策人。

输出：`docs/brief.md` 初稿。

### 1. 业务功能点台账

建立 `docs/features.csv`：

```csv
id,module,feature,description,priority,status,owner,acceptance,dependencies,notes,updated
F-001,登录,管理员登录,邮箱+密码,P0,accepted,张三,正确账号可登录；错误不泄露账号是否存在,,,2026-11-20
```

- ID：`F-001`，只增不改；
- 状态：`idea / scoped / in-progress / blocked / demo / accepted / deferred / cut`；
- 优先级：`P0 / P1 / P2`；
- `acceptance` 必须可验证；
- 依赖用 `;` 分隔。

### 2. 业务语义补充

按需维护：

- `docs/glossary.md`：术语、别名、易混淆点；
- `docs/state-machines.md`：状态、转换、不变量；
- `docs/permissions.md`：角色 × 能力矩阵。

### 3. 切片与路线图

在 `docs/roadmap.md` 排里程碑和垂直切片：

```text
S1：登录 → 列表
S2：新建/编辑 → 列表刷新
S3：导入 → 对账
```

每个切片必须：

- 能独立演示；
- 有明确验收人；
- 不跨太多模块。

### 4. 开发/演示循环

- 每天选择切片内功能点；
- 完成后更新 `features.csv` 状态；
- 每次演示/沟通追加 `docs/delivery-log.md`；
- 阻塞立即记录并升级。

### 5. 验收

- 按 `docs/acceptance.md` 逐项验证；
- 证据：截图、录屏、测试记录、对账结果；
- 遗留问题写清楚，决定“通过/有条件通过/不通过”。

### 6. 交接

填 `docs/handoff.md`：

- 代码仓库、部署目录、环境、账号位置；
- 运行/发布/回滚/备份；
- 已知问题、待办；
- 文档索引。

### 7. 复盘与回灌

- 哪些做对了、哪些返工；
- 更新相关 Skill 的 references/assets/scripts；
- 记录反模式；
- 升版本并写 README 版本记录。

## 文档契约

| 文件 | 作用 | 维护时机 |
|---|---|---|
| `docs/brief.md` | 背景、目标、范围、Non-goals、干系人、风险 | 项目开始、范围变化 |
| `docs/features.csv` | 功能点台账（唯一事实源） | 每次状态/范围变化 |
| `docs/glossary.md` | 术语表 | 新术语出现 |
| `docs/state-machines.md` | 状态与转换 | 状态/流程变化 |
| `docs/permissions.md` | 角色与能力 | 权限变化 |
| `docs/decisions.md` | 关键决策与代价 | 每个重要选择 |
| `docs/roadmap.md` | 里程碑、切片、下一次开工 | 每个阶段 |
| `docs/delivery-log.md` | 开发/沟通/演示/阻塞/变更 | 每天或每次事件 |
| `docs/acceptance.md` | 验收标准、证据、结论 | 验收时 |
| `docs/handoff.md` | 交接清单 | 交接时 |

## 工具

```bash
# 生成 docs 模板
python .claude/skills/fde-delivery/scripts/scaffold.py ../my-project \
  --name my-project \
  --title "我的项目"

# 校验功能点台账
python .claude/skills/fde-delivery/scripts/feature_lint.py docs/features.csv
python .claude/skills/fde-delivery/scripts/feature_lint.py docs/features.csv --strict
```

`feature_lint` 检查：

- ID 格式与重复；
- 必填字段；
- 状态/优先级；
- owner 与 acceptance；
- 依赖存在且不自依赖；
- 输出状态/优先级汇总。

## 硬性规则

- 没有 `brief.md` 的范围和 Non-goals，不开工。
- 每个功能点必须有 ID、验收标准、状态；`accepted` 必须有 owner 和 acceptance。
- 状态变更必须更新 `features.csv`；不要只在聊天里说。
- 范围变更必须同时更新 `features.csv`、`roadmap.md`、`delivery-log.md`；影响架构的加 `decisions.md`。
- 文档只放一个事实源；不要在多个文档复制同一张表。
- 验收必须有证据；没有证据不算完成。
- 交接必须写清楚环境、账号位置、运行/回滚、已知问题。
- 项目结束必须回灌 Skill；只写项目文档不算沉淀。

## 质量门禁

- `feature_lint` 无 ERROR；WARN 已确认；
- `brief.md` 有目标、范围、Non-goals、干系人；
- 每个里程碑至少一个可演示切片；
- 演示记录、验收记录、交接文档齐全；
- 关键决策有记录；
- 下次开工步骤明确；
- Skill 回灌完成（如适用）。

## 资源索引

### references（按需加载）

- `references/delivery-model.md`：FDE 工作方式、角色、节奏、决策权、反模式。
- `references/intake.md`：需求访谈问题库、范围、Non-goals、风险、估算。
- `references/feature-map.md`：能力地图、功能点台账、状态、验收标准、依赖、追踪。
- `references/docs-contract.md`：文档事实源、维护时机、与其他 Skill 的衔接。
- `references/delivery-loop.md`：切片选择、日/周节奏、演示、阻塞、变更协议。
- `references/acceptance-and-handoff.md`：UAT、证据、交接清单、运行手册。
- `references/knowledge-capture.md`：复盘、Skill 回灌、反模式、版本化。

### assets

- `assets/docs-templates/`：brief、features.csv、glossary、state-machines、permissions、decisions、roadmap、delivery-log、acceptance、handoff。

### scripts

- `scripts/scaffold.py`：把文档模板复制到项目 `docs/`。
- `scripts/feature_lint.py`：校验 `features.csv`。

## 不要做的事

- 不要在范围没定的时候直接写代码；
- 不要用聊天记录代替功能点台账；
- 不要把所有功能点都标 P0；
- 不要没有验收标准就标 `accepted`；
- 不要让范围变更静默发生；
- 不要等项目结束才补文档；
- 不要把项目文档复制成 Skill；回灌要提炼成规则/模板/脚本。
