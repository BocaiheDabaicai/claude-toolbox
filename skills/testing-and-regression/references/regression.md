# 回归与发布门禁

## 1. 回归范围

每次发布至少：

- 构建；
- 单元/组件/API 测试；
- 类型检查；
- 关键 E2E；
- 健康检查；
- 数据迁移对账（如适用）；
- 回滚验证（重要发布）。

## 2. gate.py

`gate.toml`：

```toml
[project]
name = "crm"
report = "docs/regression-report.md"

[[checks]]
name = "frontend-build"
type = "command"
command = "pnpm build"
cwd = "apps/web"
timeout = 600

[[checks]]
name = "backend-tests"
type = "command"
command = "uv run pytest"
cwd = "services/api"

[[checks]]
name = "api-health"
type = "http"
url = "http://127.0.0.1:8000/api/healthz"
expect_status = 200
```

运行：

```bash
python scripts/gate.py --config gate.toml --list
python scripts/gate.py --config gate.toml --dry-run
python scripts/gate.py --config gate.toml
python scripts/gate.py --config gate.toml --only backend-tests
```

- 命令来自本地可信配置；
- `--dry-run` 只打印；
- 失败退出码 1；
- 报告写 Markdown；
- `--json` 供 CI 使用。

## 3. 检查类型

| 类型 | 用途 |
|---|---|
| `command` | 构建、测试、lint、迁移 |
| `http` | healthz/readyz、关键接口 |
| `file` | 配置/证书/构建产物是否存在 |

## 4. 发布流程

1. 功能点 `accepted`；
2. `gate.py` 全绿；
3. 备份；
4. 迁移；
5. 部署；
6. 健康检查；
7. 主链路冒烟；
8. 观察期；
9. 回滚预案。

## 5. 热修复

- 只改必要代码；
- 补一个回归用例；
- 走最小门禁（构建 + 关键测试 + 健康检查）；
- 发布后补完整回归；
- 记录原因和影响。

## 6. 回滚验证

- 回滚命令可执行；
- 回滚后健康检查；
- 回滚后主链路；
- 数据迁移回滚方案；
- 记录时间线。

## 7. 报告

`docs/regression-report.md`：

- 检查列表/结果/耗时；
- 失败输出；
- 手工回归；
- 证据；
- 结论/签字。
