# E2E

## 1. 只测关键链路

- 登录/退出/过期；
- 第一个业务闭环（列表 → 创建 → 编辑 → 删除）；
- 支付/订单/迁移等高风险流程；
- 权限/未登录；
- 关键空态/错误态。

不要用 E2E 覆盖所有表单校验/样式。

## 2. 选择器

优先级：

1. `getByRole` / `getByLabel` / `getByText`（可访问性）；
2. `data-testid`；
3. CSS 结构（最后手段）。

给关键元素加稳定 `data-testid`，避免文案改了就挂。

## 3. 稳定性

- 不用 `waitForTimeout`；
- 用 `expect(locator).toBeVisible()` 自动等待；
- 固定测试数据/账号；
- 每个用例独立登录/清理；
- 不依赖执行顺序；
- 外部服务 mock 或测试环境。

## 4. 配置

`playwright.config.ts`：

- `baseURL` 从环境变量；
- `trace: 'on-first-retry'`；
- `screenshot: 'only-on-failure'`；
- CI 重试 1–2 次；
- 桌面 + 移动 viewport（按形态）。

## 5. CI

```bash
pnpm exec playwright test
```

- 失败上传 trace/screenshot；
- flaky 用例隔离并记录；
- 关键链路失败阻断发布；
- 不在 CI 里连生产。

## 6. 登录态

- 用存储态复用（`storageState`）减少登录次数；
- 但至少保留一个真实登录用例；
- token 过期/退出单独测。

## 7. 常见问题

| 问题 | 处理 |
|---|---|
| 元素找不到 | 用 role/testid，检查 SSR/加载 |
| 偶发失败 | 去 sleep，加自动等待，隔离数据 |
| 数据污染 | 独立账号/清理 |
| 慢 | 只跑关键链路，拆分项目 |
| 环境差异 | 固定 viewport/时区/语言 |
