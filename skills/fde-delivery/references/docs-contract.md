# 文档契约

## 1. 事实源

| 文档 | 唯一负责的内容 | 不在这里写 |
|---|---|---|
| `brief.md` | 背景、目标、范围、Non-goals、干系人、风险 | 功能点明细 |
| `features.csv` | 功能点、状态、owner、验收、依赖 | 技术方案 |
| `glossary.md` | 术语定义 | 业务规则长文 |
| `state-machines.md` | 状态、转换、不变量 | 页面布局 |
| `permissions.md` | 角色/能力矩阵 | 接口字段 |
| `decisions.md` | 决策、背景、备选、代价 | 日常进度 |
| `roadmap.md` | 里程碑、切片、下一次开工 | 详细需求 |
| `delivery-log.md` | 每天/每次事件 | 长期结论（放 decisions） |
| `acceptance.md` | 验收标准、证据、结论 | 开发计划 |
| `handoff.md` | 交接信息 | 需求变更 |

原则：**同一事实只写一处，其他地方链接。**

## 2. 维护时机

| 事件 | 更新 |
|---|---|
| 项目开始 | brief、features 初稿、roadmap |
| 需求澄清 | features、glossary、state-machines、permissions |
| 技术选型 | decisions |
| 每次开发/演示 | delivery-log、features 状态 |
| 范围变更 | features、roadmap、delivery-log，必要时 decisions |
| 验收 | acceptance、features 状态 |
| 交接 | handoff |
| 复盘 | 相关 Skill 的 references/assets/scripts |

## 3. 与其他 Skill 的衔接

- `frontend-h5-project`：`brief/features` 决定页面范围；`state-machines/permissions` 约束交互；`roadmap` 排页面切片。
- `nuxt-fullstack`：`features` 决定业务域和 CRUD；`decisions` 记录架构选择。
- `fastapi-service`：`features` 决定接口；`permissions` 决定鉴权；`state-machines` 决定状态流转。
- `data-migration`：`features` 中的迁移范围；`glossary` 统一字段语义；`decisions` 记录映射规则。
- `python-service-ops`：`handoff` 记录部署/启停/健康检查。

## 4. 命名与格式

- 文件名固定，不放日期（日期写在内容里）；
- 功能点 ID `F-001`，决策 `D-001`；
- 日期 `YYYY-MM-DD`；
- CSV 用 UTF-8，逗号分隔，字段内逗号加引号；
- Markdown 表格保持简短，长内容用列表/小节。

## 5. 更新规则

- 状态变更：先改 `features.csv`，再在 `delivery-log` 写一句；
- 范围变更：`features` + `roadmap` + `delivery-log`；影响架构加 `decisions`；
- 验收：`acceptance` + `features`；
- 交接：`handoff` + 相关运行文档；
- 复盘：只提炼规则/模板/脚本，不复制整份项目文档。

## 6. 反模式

- 同一张功能表在 brief、roadmap、confluence 各一份；
- 功能点状态只在群里说；
- 决策只存在脑子里；
- 文档写完不更新；
- 项目结束才补验收/交接。
