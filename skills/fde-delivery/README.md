# fde-delivery

FDE 交付 Skill：需求 intake、业务功能点台账、垂直切片、演示、验收、交接和知识回灌。

## 适用场景

- 新项目/新需求开始，需要快速定范围；
- 业务描述模糊，需要拆功能点；
- 多人协作，需要统一文档契约；
- 需要排里程碑、垂直切片和验收；
- 需要交接和复盘。

## 快速开始

```bash
# 1. 生成 docs 模板
python .claude/skills/fde-delivery/scripts/scaffold.py ../my-project \
  --name my-project \
  --title "我的项目"

# 2. 填 brief 和 features.csv
#    docs/brief.md
#    docs/features.csv

# 3. 校验功能点台账
python .claude/skills/fde-delivery/scripts/feature_lint.py docs/features.csv

# 4. 按 roadmap 的垂直切片推进
#    每次演示/沟通更新 docs/delivery-log.md
#    验收更新 docs/acceptance.md
#    交接更新 docs/handoff.md
```

## 文档

| 文件 | 作用 |
|---|---|
| `brief.md` | 背景、目标、范围、Non-goals、干系人、风险 |
| `features.csv` | 功能点台账（唯一事实源） |
| `glossary.md` | 术语表 |
| `state-machines.md` | 状态与转换 |
| `permissions.md` | 角色与能力矩阵 |
| `decisions.md` | 关键决策与代价 |
| `roadmap.md` | 里程碑、切片、下一次开工 |
| `delivery-log.md` | 开发/沟通/演示/阻塞/变更 |
| `acceptance.md` | 验收标准、证据、结论 |
| `handoff.md` | 交接清单 |

## 功能点状态

`idea` → `scoped` → `in-progress` → `demo` → `accepted`

异常/结束：

- `blocked`：阻塞，必须有 owner；
- `deferred`：暂缓，notes 写原因；
- `cut`：砍掉，notes 写原因。

## 检查

```bash
python scripts/feature_lint.py docs/features.csv --strict
```

检查 ID、必填字段、状态、优先级、owner、acceptance、依赖和汇总。

## 目录

```
fde-delivery/
├─ SKILL.md
├─ README.md
├─ references/              # 交付模型、intake、功能点、文档契约、循环、验收、回灌
├─ assets/docs-templates/   # 10 份文档模板
├─ scripts/                 # scaffold / feature_lint
└─ tests/                   # unittest
```

## 版本记录

| 版本 | 日期 | 内容 |
| --- | --- | --- |
| 0.1.0 | 2026-11-20 | 初始版本：文档模板、scaffold、feature_lint、交付/验收/交接/回灌参考；11 个测试通过 |
