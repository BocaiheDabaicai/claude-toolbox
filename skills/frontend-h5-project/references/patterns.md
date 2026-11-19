# 已验证模式与业务坑

> 这些模式来自真实项目（会员商城、返利项目）的联调与回归，优先复用，不要重新发明。

## 1. 本地优先购物车（电商项目）

### 1.1 为什么

购物车加减如果每次都请求接口，会出现：

- 每次点击都发请求，弱网下交互卡顿；
- 并发请求返回顺序错乱，数量回跳；
- 服务端购物车与页面状态不同步。

因此：**浏览期只读写 localStorage，结算时才与服务端同步。**

### 1.2 数据源

```
localStorage key: <prefix>_cart_items_<storeId>
```

按店铺隔离：切换店铺后读取该店铺的购物车，避免跨店串数据。

单条 item 结构：

```js
{
  key: `${goodsId}_${skuId || ''}`,
  goodsId,
  skuId,
  single: Boolean,
  num,
  price,
  linePrice,
  name,
  logo,
  specText,
  stock,
}
```

### 1.3 Store 接口

```js
// stores/cart.js（选项式）
state: () => ({ items: [], loaded: false, storeId: 0 })
getters: {
  effectiveTotalNum,
  badge,                 // 99+
  hasItems,
  displayQuantityOf,     // 某商品在购物车中的总件数
}
actions: {
  load(),                // 读当前店铺 localStorage，无接口
  persist(),             // 写回 localStorage
  setQuantityForGoods(), // 单规格直接设置总量
  addSkuItem(),          // SKU 加购，同 SKU 累加并受库存封顶
  setItemQuantity(),     // 购物车页改数量
  removeItems(keys),     // 删除本地条目
  async flushForCheckout(), // 结算时同步到服务端
  finishCheckout(keys),  // 提交成功后只移除本次结算的本地条目
  reset(),               // 退出登录/切店时清空
}
```

### 1.4 结算同步顺序

```
购物车页勾选商品
  → flushForCheckout()
      1. cart/save/all（action='=' 幂等 upsert，第一项必须带 userId）
      2. 用返回的 cartIdList 调 cart/list
  → 按 goodsId + skuId 匹配勾选项，只把勾选商品的 cartIds 传给 /checkout
  → 预订单提交成功（后端删除本次 cartIds）
  → finishCheckout(keys) 只移除本次勾选的本地条目
```

关键点：

- `cart/save/all` 的 `userId` 从登录会话 `getUserId()` 读取，禁止由调用方随意传入。
- `action='='` 是幂等 upsert，不会重复累加。
- **不要**在部分结算时调用 `cart/clear`（空参数会清空当前会员全部购物车）。
- 未勾选商品必须保留在本地与服务端，下次结算还能用。
- 结算页（`CheckoutView`）用 `cart/list` 的返回作为展示与金额来源，提交金额由后端按商品原价重算。

### 1.5 常见坑

- `cart/clear` 不传 `cartId` 会清空全部；
- `preOrder/submit` 会删除传入的全部 `cartIds`，后端未校验 userId；
- `createPreOrder` 按 `goodsId` 去重，同商品多 SKU 可能只剩一条；
- 预订单提交阶段**不校验库存**，前端必须在结算前把关；
- 预订单金额不含会员折扣、卡券、积分。

## 2. 结算模式（cart / buyNow / reorder）

`CheckoutView` 用 `route.query.mode` 区分三种入口：

| mode | 来源 | 展示数据 | 提交参数 |
| --- | --- | --- | --- |
| `cart`（默认） | 购物车勾选 | `cart/list` + `cartIds` | `{ remark, cartIds }` |
| `buyNow` | 商品详情立即购买 | `cart/list` + 单商品直购参数 | `{ remark, goods: [{ goodsId, skuId, num }] }` |
| `reorder` | 预订单「再下一单」 | 逐项 `cart/list` 合并 | `{ remark, goods: [...] }` |

提交成功后的清理：

- `cart`：后端删除本次 cartIds → 前端 `finishCheckout(keys)` 只删本地对应条目；
- `buyNow` / `reorder`：不碰本地购物车；`reorder` 额外清理 sessionStorage 缓存。

## 3. 「再下一单」与库存校验

预订单详情从 `goodsList[]` 取 `goodsId / skuId / num`，按下述流程处理：

1. 逐项调用 `cart/list` 直购参数（`{ goodsId, skuId, buyNum, orderMode: 'oneself' }`）。
   - `cart/list` 直购模式一次只支持一个商品，需并发请求后合并。
   - `isEffect === false` 表示库存不足/商品失效。
2. 库存不足时调用 `goodsApi/detail`，取**商品级库存与 SKU 级库存的较小值**，按可售数量下调后再次用 `cart/list` 校验。
   - 商品详情接口同时返回 `stock` 与 `skuList[].stock`；后端 `cart/list` 的 `isEffect` 主要看商品级库存，SKU 场景要取两者较小值。
3. 售罄/下架条目剔除；有调整/移除时用确认弹窗说明，确认后继续。
4. 校验后的 `{ goodsId, skuId, num }[]` 写入 sessionStorage，跳 `/checkout?mode=reorder`。
5. 结算页重新逐项拉取最新数据：
   - 任一行缺失（下架/售罄）→ 报错并返回预订单，不允许提交旧数据；
   - 某行 `isEffect === false` → 展示失效并禁用提交；
6. 提交走 `preOrder/submit` 的 `goods` 数组；成功后清理 sessionStorage 并跳新预订单详情。

> 预订单创建本身不校验库存，即使前端遗漏，后端也不会拦截；库存把关必须在前端完成。

## 4. 登录前店铺/商户初始化

```js
// stores/config.js
let initPromise = null
actions: {
  async ensureInitialized() {
    if (this.storeId > 0) return this.storeInfo
    if (!initPromise) {
      initPromise = getSystemConfig({ silent: true })
        .then((res) => this.applySystemConfig(res.data))
        .finally(() => { initPromise = null })
    }
    return initPromise
  },
}
```

路由守卫第一步调用：

```js
const configStore = useConfigStore()
if (!configStore.hasStore) {
  await configStore.ensureInitialized().catch(() => {})
}
```

适用场景：登录接口要求 `storeId != 0`、会员按 store 过滤、页面请求依赖商户号。并发去重（模块级 `initPromise`）避免多个请求同时初始化。

## 5. 动态返回

- 路由 `meta.backTo` 支持字符串或数组。
- `PageHeader` 把 `backTo` 路由的 `:id` 转成正则，匹配上一页路径：
  - 匹配 → `router.back()`，保留滚动/历史；
  - 不匹配 → 跳数组第一项，避免停留在兄弟页面。
- 从购物车进商品详情，详情返回应回购物车；`goodsDetail` 的 `backTo` 要包含 `cart`。
- 售后详情可能来自订单列表或订单详情，`backTo: ['orderList', 'orderDetail']`。

## 6. 旧路径映射

banner、navigation、文章、旧分享链接可能仍是 `pages/xxx` 路径。集中维护：

```js
// router/legacy.js
export function resolveLegacyUrl(url) {
  if (!url) return null
  const [path, query = ''] = String(url).split('?')
  const params = new URLSearchParams(query)
  if (path === 'pages/article/detail') {
    return { name: 'article', params: { articleId: params.get('articleId') } }
  }
  if (path === 'pages/goods/detail') {
    return { name: 'goodsDetail', params: { goodsId: params.get('goodsId') } }
  }
  // ...
  return null
}
```

页面只调用 `resolveLegacyUrl`，不要散落判断。无法映射外链时再 `window.open`。

## 7. 富文本清洗

后端富文本（文章、商品详情）不能直接 `v-html`。使用白名单清洗：

```js
// utils/sanitize.js
const ALLOWED_TAGS = new Set(['P','BR','DIV','SPAN','STRONG','B','EM','I','U','UL','OL','LI','H1'...])
const ALLOWED_ATTR = new Set(['href','src','alt','title','target','rel','colspan','rowspan'])

export function sanitizeHtml(html) {
  const doc = new DOMParser().parseFromString(String(html || ''), 'text/html')
  // 遍历节点：移除不在白名单的标签（保留文本），移除事件属性与 javascript: URL
  return doc.body.innerHTML
}
```

- 标签、属性都用白名单，不要用黑名单。
- 图片 `src` 允许 http/https/data；链接 `href` 禁止 `javascript:`。
- 渲染容器用 `.rich-text` 统一样式。
- 建议后端再做一次富文本白名单校验。

## 8. 金额与日期

### 8.1 金额

```js
import Big from 'big.js'
formatAmount(value)        // ¥1,234.50（2–4 位小数，千分位）
formatSignedAmount(value)  // +¥10.00 / -¥5.00
formatPercent(value)       // 12.5%
sumAmounts(list, pick)
```

- 禁止用浮点数直接相加/比较；用 `Big`。
- 展示统一走 `utils/money.js`，页面不要自己 `toFixed(2)`。
- 后端金额可能是字符串，`Big` 能安全处理。

### 8.2 日期

- `formatDateTime(value)` 兼容：
  - `yyyy-MM-dd HH:mm:ss` 字符串；
  - 10 位秒级时间戳；
  - 13 位毫秒时间戳；
  - `Date` 实例。
- 统一裁到分钟，列表里不要出现秒。
- 生日选择用 `DatePickerDialog`，设置 `minDate` 与年份快速跳转。

## 9. 分页与请求竞态

- 分页返回结构不统一：`{ content, totalElements }`、`{ list, total }`、`{ data: { content } }` 都见过，在 api 层归一化。
- 无限加载用 `LoadMoreSentinel`，`rootMargin: '240px'` 提前触发。
- 切 tab / 改筛选时给请求加 `requestToken`，旧响应回来直接丢弃。
- 页面级错误用 `silent: true` + 页内错误态；请求层默认 toast 只用于一次性操作。

## 10. 图片加载

- 占位：品牌渐变或 `--brand-gradient-air`，不要长时间空白/灰块。
- 淡入：`transition-opacity duration-500`，`@load` 后 `opacity-100`。
- 失败：`@error` 后隐藏图片，保留渐变/首字兜底。
- 列表项每条独立 `loaded` / `failed`，key 用业务稳定标识。
- 轮播图：后台无图/加载失败可用本地备用图；自动轮播等当前图与下一张图都就绪后再切换，避免空白帧。

## 11. 跨页数据传递

- 简单参数用 `route.query` / `route.params`。
- 复杂/敏感数据用 `sessionStorage`，带固定 key 和读写校验函数：

```js
saveReorderPayload({ goods, sourcePreOrderId })
readReorderPayload()   // 解析 + 校验 + 归一化，非法返回 null
clearReorderPayload()  // 提交成功后清理
```

- 读取时统一做数值归一化（`goodsId > 0`、`num >= 1`），不要信任存储内容。
- 隐私模式可能禁用 storage，写入要 try/catch；读取失败时给出可恢复的错误态。

## 12. 安全

- 需要当前会员归属的接口，`userId` 从登录会话读取，不接受调用方传入。
- 登录回跳的 `redirect` 参数必须用 `utils/redirect.js` 的 `safeRedirect` 校验：只允许以 `/` 开头、不是 `//`、不含协议与反斜杠的站内路径，避免开放重定向。
- 富文本必须白名单清洗。
- 不要把 token、手机号、身份证等敏感信息写进 URL。
- 预订单/订单/售后详情接口若后端未校验归属，前端不要用可枚举 ID 做敏感展示；联调时记录风险并推动后端修复。
- 上传文件限制类型与大小（如单张 ≤ 2MB），上传结果取 `data.url`，不要误用文件 ID。

## 13. 后端契约坑清单（迁移时逐项确认）

- [ ] 登录是否要求非 0 `storeId`；
- [ ] 会员是否按 store 过滤；
- [ ] token 过期是 `code=1001` 还是 HTTP 401；
- [ ] 分页字段是 `content/totalElements` 还是 `list/total`；
- [ ] 图片地址端口是否与接口不同；
- [ ] 上传返回 `url` 还是文件 ID；
- [ ] 购物车清空接口空参数是否清空全部；
- [ ] 预订单提交是否校验库存、是否按 goodsId 去重；
- [ ] 取消订单/去支付入口是否在旧项目已注释；
- [ ] 富文本是否需要清洗；
- [ ] CORS 是否允许自定义 header；
- [ ] 测试服证书是否覆盖使用的域名/IP。

## 14. 选择器类弹窗

- `StorePickerDialog`：搜索 + 当前标记 + 距离/地址；选择后写默认店铺并刷新页面数据。
- `SkuPopup`：
  - `normalizeSkuGoods` 统一单规格/多规格；
  - `specIds` 用 `-` 分隔，顺序与 `specList` 对应；
  - 规格值的可用性由「当前选择下是否还有有库存的 SKU」决定；
  - 加购与立即购买复用同一套选择结果，由 `mode` 区分动作。
- 弹窗打开时锁定 body 滚动；关闭恢复；点击遮罩关闭，内容区 `@click.stop`。
