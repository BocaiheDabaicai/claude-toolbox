# 质量与验收

## 1. 命令

```bash
pnpm check           # 边界检查 + nuxt typecheck
pnpm build           # 生产构建
pnpm db:generate     # 应无 schema 变更
pnpm db:seed         # 本地/测试环境
```

## 2. 合并前门禁

- `pnpm check` 通过；
- `pnpm build` 通过；
- `pnpm db:generate` 无意外新迁移；
- 无 `console.log` 调试输出（错误日志除外）；
- `pnpm-lock.yaml` 无非预期改动；
- 新增接口有 Zod 校验和错误结构；
- 新增页面有加载/空/错误态。

## 3. 功能回归

- 未登录访问业务页 → 跳登录；
- 登录成功 → 回跳原页面；
- 登录失败 → 提示，不泄露账号是否存在；
- 退出 → Cookie 清除，回登录；
- 列表：搜索、分页、空态、错误态；
- 创建：必填校验、邮箱格式、保存后刷新；
- 编辑：回填、保存、取消；
- 删除：二次确认、软删、列表刷新；
- `/api/healthz` 200；
- `/api/readyz` 在数据库可用时 200。

## 4. 安全

- 客户端代码不包含数据库地址、会话密钥、密码 hash；
- 所有写接口有 `requireSameOrigin`；
- 所有输入服务端校验；
- 错误响应不含堆栈；
- `.env` 不入库；
- 生产 Cookie `Secure`；
- 反向代理保留 Host / 设置 `X-Forwarded-Host`。

## 5. 性能

- 列表只查需要的列（数据量大时用 `select({ ... })`）；
- 分页有上限；
- 搜索字段有索引；
- 避免 N+1；
- 大字段（备注、富文本）不在列表里全量返回；
- 慢查询用 `EXPLAIN ANALYZE` 确认索引。

## 6. 响应式与可访问性

- 320 / 768 / 1280 宽度检查；
- 表单控件有 label；
- 按钮有可读文本或 aria-label；
- 颜色对比度满足正文可读；
- 键盘可完成登录/表单/弹窗关闭。

## 7. 测试策略

当前模板以类型检查、构建和手工主链路为主。后续可补：

- 纯函数单测（校验、格式化、密码）；
- API 集成测试：使用独立测试 database，跑迁移 + seed + 调用 `/api/**`；
- Playwright：登录 → 创建客户 → 编辑 → 删除；
- 契约测试：响应结构固定为 `{ code, message, data }`。

## 8. 版本固定说明

- `nuxt` 固定 4.5.2：Node 22.19+/24.11+，peer 依赖干净；
- `daisyui` 固定 5.7.28：5.8.x 在 Nuxt 4.5 / Vite 7 下会产生 CSS `calc()` 解析警告；
- `typescript` 5.9.3：与 `vue-tsc` 3.3.x 稳定配合；
- 升级依赖时先跑 `pnpm check && pnpm build`，确认无新增警告。
