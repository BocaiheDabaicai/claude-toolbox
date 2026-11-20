# testing-and-regression

测试与回归 Skill：Vitest / pytest / Playwright / 契约测试 / 发布门禁。

## 适用场景

- 新项目测试策略；
- 前端单元/组件/E2E；
- FastAPI pytest/契约；
- 数据迁移对账；
- 发布前回归门禁；
- 测试计划/回归报告/发布清单。

## 快速开始

```bash
# 1. 生成 gate.toml 与 docs
python .claude/skills/testing-and-regression/scripts/scaffold.py ../my-project \
  --name my-project \
  --title "我的项目"

# 2. 修改 gate.toml 的 cwd / command / URL
# 3. 预演
python .claude/skills/testing-and-regression/scripts/gate.py --config gate.toml --dry-run

# 4. 执行
python .claude/skills/testing-and-regression/scripts/gate.py --config gate.toml
```

## 模板

| 目录 | 内容 |
|---|---|
| `assets/templates/gate.toml` | 门禁配置示例 |
| `assets/templates/frontend/` | vitest.config、setup、示例测试、playwright.config、E2E |
| `assets/templates/backend/` | FastAPI httpx conftest、health 测试 |
| `assets/docs-templates/` | test-plan、regression-report、release-checklist |

## gate.py

支持：

- `command`：构建、测试、lint、迁移；
- `http`：healthz/readyz、关键接口；
- `file`：配置/构建产物是否存在；
- `--only`、`--fail-fast`、`--dry-run`、`--json`、`--list`；
- Markdown 报告。

## 目录

```
testing-and-regression/
├─ SKILL.md
├─ README.md
├─ references/              # 策略、前端、后端、契约、E2E、回归、指标
├─ assets/
│  ├─ templates/            # gate.toml、frontend、backend
│  └─ docs-templates/       # 测试计划、回归报告、发布清单
├─ scripts/                 # gate.py、scaffold.py
└─ tests/                   # gate 的 unittest
```

## 版本记录

| 版本 | 日期 | 内容 |
| --- | --- | --- |
| 0.1.0 | 2026-11-20 | 初始版本：测试策略、Vitest/Playwright/pytest 模板、契约/E2E/回归参考、gate.py 门禁与 7 个测试 |
