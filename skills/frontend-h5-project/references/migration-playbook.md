# 旧项目迁移手册

> 适用：Vue2 / uni-app / HBuilderX / uview 等旧前端，迁移到 Vue3 + Vite + Tailwind 的 H5 项目。
> 核心原则：**先盘点、再定契约、分阶段迁移、每阶段验收。**

## 1. 阶段 0：盘点与范围

### 1.1 路由盘点

统计旧项目 `pages.json` / 路由表，把每个页面归入三类：

| 分类 | 判定 | 处理 |
| --- | --- | --- |
| 在用 | 界面上显示、能点击进入、实际在用 | 迁移 |
| 条件可达 | 依赖配送/预约/支付/会员卡等开关 | 默认不做，记录条件 |
| 排除 | 置灰、注释、无入口、商户专用 | 不迁，写明原因 |

产出 `docs/pages.md`：

- 总数与分类数量；
- 在用页面表（旧路径 / 新路由 / 入口 / 主要接口）；
- 条件页与排除页清单；
- 底部导航映射；
- 旧路径 → 新路径映射。

### 1.2 先问清楚

- 迁移范围：哪些页面必须做，哪些可以砍；
- 多端：是否还需要小程序/App；
- 后端：地址、环境、证书、是否允许直接调现有接口；
- 品牌：是否沿用现有配色，还是换主题；
- 支付/配送/预约/卡券：是否在本次范围。

## 2. 阶段 0.5：契约调研

按 `backend-contract.md` 的调研顺序，产出 `docs/backend-contract.md`：

- 请求头、响应结构、错误码；
- 登录流程与 storeId/merchantNo 初始化；
- 每个页面的接口清单；
- 分页、上传、状态枚举；
- 已知后端坑。

**没有契约文档，不要开始写页面。**

## 3. 阶段 1：工程骨架

1. 用 Skill 的 `scripts/scaffold.mjs` 生成骨架，或复制 `assets/template`；
2. 修改 `.env.development` / `.env.production` 的接口地址与标题；
3. `pnpm install`、`pnpm dev`、`pnpm build` 三连验证；
4. 确认 `pnpm-lock.yaml` 首行为 9.x，且没有非预期 diff；
5. 修改 `AGENTS.md` / `CLAUDE.md` 的项目名与约束（如需要）。

## 4. 阶段 2：基础设施

- `utils/request.js`：按契约实现请求头、响应判断、登录过期；
- `utils/auth.js`：token / userId 存取，key 加项目前缀；
- `stores/user.js`：登录、getInfo、logout、reset；
- `stores/config.js`（如需要）：登录前初始化 storeId / merchantNo；
- `router/index.js`：初始化 → 未登录 → 恢复用户 → 已登录不进登录页；
- `router/legacy.js`：旧路径映射；
- 全局 Toast / Confirm / Skeleton / LoadMore。

验收：清空 localStorage 后，登录页能拿到验证码并登录；请求头在 Network 可见。

## 5. 阶段 3+：页面迁移顺序

按依赖关系推进，不要从边缘页面开始：

1. **登录页**：验证码、账号/短信、redirect 回跳；
2. **首页**：banner、金刚区、商品列表、店铺切换；
3. **基础购买链路**：分类/微店 → 商品详情 → SKU → 购物车 → 结算 → 预订单；
4. **订单与售后**：列表 → 详情 → 确认收货 → 申请售后 → 售后详情；
5. **个人中心与资产**：我的 → 个人信息/密码/手机号 → 会员码 → 钱包/积分；
6. **内容页**：文章详情、消息（可选）。

每个阶段只做一组页面，先确认范围再动手。

## 6. 每阶段工作循环

```
实现页面
  → pnpm build
  → mock 或真实后端验证主链路 / 库存 / 空态 / 错误态
  → 更新 docs/roadmap.md 开发日志与「下一次开工步骤」
  → 询问是否提交（默认只本地提交，不推送）
  → 进入下一阶段
```

测试重点：

- 首屏骨架 → 内容过渡是否生硬；
- 列表分页、切 tab、筛选竞态；
- 二级页返回是否正确；
- hash 路由刷新/直开是否正常；
- 图片加载/失败兜底；
- 320 / 375 / 414 宽度。

## 7. uni-app → Web 对照

| 旧项目 | 新项目 |
| --- | --- |
| `uni.request` / 自定义 request | axios + 拦截器 |
| `uni.getStorageSync` | `localStorage`（统一 utils/store） |
| `uni.navigateTo` / `switchTab` | `router.push` / tab 路由 |
| `uni.showToast` / `showModal` | `toast` / `confirm` + 全局挂载 |
| `mescroll` | 页面滚动 + `LoadMoreSentinel` |
| `uview-ui` 组件 | daisyUI + Tailwind 自建 |
| `goods-sku-popup` | Vue3 版 `SkuPopup` |
| `jyf-parser` 富文本 | `sanitizeHtml` + `v-html` + `.rich-text` |
| `uni.getLocation` | `navigator.geolocation`（失败静默） |
| `uni.setClipboardData` | `navigator.clipboard.writeText` + `execCommand` 兜底 |
| 微信 JSAPI / 招行支付 | 本期不做（先确认后端行为） |

## 8. 范围纪律

- 置灰/注释/无入口的页面不要“顺手做”；
- 条件页默认不做，除非业务确认开关已启用；
- 旧项目里已经失效的按钮（去支付、取消订单、会员升级购买）不要重新实现；
- 支付链路恢复前，必须先读旧项目支付坑记录并重新设计参数校验。

## 9. 交接与文档

`docs/roadmap.md` 必须随时可交接：

- 当前进度表；
- 开发日志（做了什么、为什么、怎么验证）；
- 「下一次开工步骤」；
- 待确认事项与后端风险；
- 回归清单。

新会话接手时，先读 README → architecture → backend-contract → pages → roadmap。

## 10. 常见陷阱

- 登录前 storeId=0，登录报“店铺号不能为空”；
- 会员按 store 过滤，切店后账号查不到；
- 图片端口与接口端口不同，误以为需要代理；
- 测试服证书不包含 IP SAN，团队应统一用域名；
- 旧 banner/文章链接仍是 `pages/xxx`；
- 旧项目全局 loading 导致并发请求互相覆盖；
- 富文本直接 `v-html` 带来 XSS；
- 购物车部分结算误清空全部；
- 预订单提交不校验库存，前端必须自己把关。
