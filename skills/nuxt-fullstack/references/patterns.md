# 业务模式

## 1. 垂直切片

每个业务域按同一顺序落地：

1. `docs/features.md` 登记功能点与验收标准；
2. `shared/schemas/<domain>.ts` 定义输入校验；
3. `server/database/schema.ts` 加表/字段；
4. `pnpm db:generate` 生成迁移；
5. `server/api/<domain>/` 实现列表/详情/创建/更新/删除；
6. `app/pages/<domain>/` 实现页面；
7. `pnpm check && pnpm build`；
8. 更新 `docs/roadmap.md`。

先做一条完整链路，再扩字段，不要先铺十个表。

## 2. 列表 + 搜索 + 分页

服务端：

```ts
const querySchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(20),
  search: z.string().trim().max(100).default(''),
})
```

- 先 count 再查 rows；
- 固定排序；
- 软删过滤；
- 搜索字段与索引匹配。

客户端：

```ts
const page = ref(1)
const pageSize = ref(10)
const search = ref('')
const { data, pending, refresh } = await useFetch('/api/customers', {
  query: computed(() => ({ page: page.value, pageSize: pageSize.value, search: search.value })),
  watch: [page, pageSize, search],
})
```

- 搜索输入与已应用的 `search` 分开，避免每敲一个字请求一次；
- 分页按钮只改 `page`，由 `watch` 触发；
- 删除/保存后 `refresh()`。

## 3. 创建 / 编辑弹窗

- 新建：重置表单，`editing = null`；
- 编辑：用行数据填充表单，空值转 `''`；
- 提交前 `schema.safeParse(form)`；
- 新建 POST，编辑 PUT；
- 成功后关闭并刷新；
- 失败保留输入，显示服务端 message；
- 保存中禁用按钮，防重复提交。

## 4. 软删除

```ts
await db.update(customers)
  .set({ deletedAt: new Date(), updatedAt: new Date() })
  .where(and(eq(customers.id, id), isNull(customers.deletedAt)))
```

- 列表/详情/更新都过滤 `deletedAt`；
- 删除二次确认，文案包含对象名；
- 不提供物理删除入口，除非业务明确要求。

## 5. 统一错误

服务端：

```ts
throw new ApiError(400, 'VALIDATION_ERROR', '请求参数不合法', details)
```

客户端：

```ts
catch (err: unknown) {
  const body = err as { data?: { message?: string }; message?: string }
  error.value = body.data?.message || body.message || '保存失败'
}
```

不要在页面里判断 HTTP code 分支；统一从 `message` 取可读文案。

## 6. SSR 安全的认证

- 不在 `onMounted` 里才判断登录；
- 全局中间件在 SSR 阶段就重定向；
- `useRequestFetch()` 转发 Cookie；
- 页面组件不直接读 Cookie。

## 6.1 Pinia 状态

跨页面共享状态统一用 Pinia，选项式写法（与 `frontend-h5-project` 一致）：

```ts
// app/stores/auth.ts
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as SessionUser | null,
    initialized: false,
    loading: false,
  }),
  actions: {
    async fetchUser(force = false) {
      if (this.initialized && !force) return this.user
      // SSR 用 useRequestFetch()，客户端用 $fetch
    },
  },
})
```

页面保留兼容层，避免全站改 `user.value`：

```ts
// app/composables/useAuth.ts
import { storeToRefs } from 'pinia'
import { useAuthStore } from '~/stores/auth'

export function useAuth() {
  const store = useAuthStore()
  const { user, initialized, loading } = storeToRefs(store)
  return { user, initialized, loading, fetchUser: store.fetchUser }
}
```

规则：

- Pinia 只放跨页面共享状态（登录态、全局筛选、草稿）；
- 服务端列表/详情数据用 `useApiFetch`，不要再复制一份进 store；
- 页面局部状态用 `ref` / `reactive`；
- 不要新增全局 `useState` 作为状态管理。

## 7. Seed

- 管理员账号从环境变量读取，不硬编码；
- 示例数据只在表为空时插入；
- 可重复执行，已存在则更新管理员密码；
- 不把真实客户数据写进 seed。

## 8. 反模式

- 页面里 import `drizzle-orm` / `pg`；
- 在 `app/` 里读 `NUXT_DATABASE_URL`；
- 每个页面自己拼 `{ code, message }` 判断；
- 用 `window.location` 做登录跳转；
- 编辑时把 `null` 直接绑定到 input；
- 删除后只改本地数组，不刷新服务端分页；
- 用 `float` 算金额；
- 为每个小功能新增一套布局或颜色。
