# 前端测试

## 1. 工具

| 场景 | 工具 |
|---|---|
| 纯函数/组合式 | Vitest |
| Vue 组件 | Vitest + `@vue/test-utils` |
| Nuxt 页面/组合式 | Vitest + `@nuxt/test-utils` |
| E2E | Playwright |
| 类型 | `vue-tsc` / `nuxt typecheck` |
| 构建 | Vite / Nuxt build |

## 2. 单元/组件

- 测行为：输入 → 输出、用户操作 → DOM；
- 不测内部实现/私有方法；
- mock 网络层（`vi.mock('@/api/...')`），不 mock 被测组件；
- 组件用 `data-testid` 或可访问角色定位；
- 每个用例清理 DOM/localStorage。

示例：

```ts
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import LoginForm from '@/components/LoginForm.vue'

describe('LoginForm', () => {
  it('shows an error when password is empty', async () => {
    const wrapper = mount(LoginForm)
    await wrapper.get('form').trigger('submit')
    expect(wrapper.text()).toContain('请输入密码')
  })
})
```

## 3. H5 / 管理台 / PC

- H5：移动宽度（320/375/414）、底部导航、safe-area；
- 管理台：侧边栏/表格/弹窗/分页，768/1280；
- PC：顶部导航/宽内容区，1024/1440；
- 三种形态共用逻辑测试，布局差异用少量 E2E/截图确认。

## 4. Nuxt

- 页面/中间件/组合式：`@nuxt/test-utils`；
- server routes 用 `$fetch`/`setup` 测；
- SSR 断言：首屏 HTML 包含关键内容；
- 注意 auto-import 在测试环境的配置；
- 类型检查 `nuxt typecheck` 作为门禁。

## 5. Playwright

- 只测关键链路；
- 用 `getByRole` / `getByLabel` / `data-testid`，避免 CSS 结构；
- 不 sleep，用 expect 自动等待；
- 每个用例独立登录/清理；
- 失败保留 trace/screenshot/video；
- CI 重试 1–2 次，flaky 用例单独隔离。

## 6. 不应依赖

- 真实生产接口；
- 真实支付/短信；
- 手工造的数据；
- 当前时间（固定 clock）；
- 网络顺序、动画时长。

## 7. 门禁

```bash
pnpm typecheck
pnpm test
pnpm build
pnpm exec playwright test
```

- 构建失败不发布；
- 类型错误不发布；
- E2E 关键链路失败不发布。
