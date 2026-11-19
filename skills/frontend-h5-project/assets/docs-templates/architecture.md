# 架构设计

> 项目：__PROJECT_TITLE__
> 更新日期：YYYY-MM-DD

## 1. 设计原则

1. 只做 H5，不做小程序条件编译。
2. 只迁移在用页面；置灰、注释、无入口页面不迁。
3. 不背旧项目包袱：不复制旧全局 loading、Vuex、散落的 localStorage 读写。
4. 接口契约以现有后端为准，差异集中在请求层处理，不改后端。
5. 移动端优先：`max-w-md` 居中、语义色、骨架屏与统一动效。

## 2. 技术栈

| 类别 | 选型 | 版本 |
| --- | --- | --- |
| 框架 | Vue | ^3.5.41 |
| 构建 | Vite | ^8.2.2 |
| 路由 | vue-router（hash） | ^5.3.1 |
| 状态 | Pinia（选项式） | ^4.0.3 |
| 样式 | Tailwind CSS 4 + daisyUI 5 | ^4.3.3 / ^5.7.28 |
| 请求 | axios | ^1.20.0 |
| 金额 | big.js | ^7.0.1 |
| 包管理 | pnpm | 9.15.9 |

## 3. 目录结构

```
src/
├─ api/          # 接口函数，按业务模块拆分
├─ assets/       # 图片与品牌色变量
├─ components/   # 通用组件
├─ layouts/      # 页面容器
├─ router/       # 路由表 + 守卫 + 旧路径映射
├─ stores/       # Pinia 状态
├─ utils/        # 请求、登录态、金额、日期、提示、清洗
└─ views/        # 页面
```

## 4. 请求层

- 单一 axios 实例，`baseURL = import.meta.env.VITE_APP_BASE_API`。
- 请求头统一注入（token、商户/店铺、平台、定位等按后端要求）。
- 响应结构：

```json
{ "code": 200, "message": "操作成功", "data": {} }
```

- 约定：
  - `code === 200` 成功，返回响应体；
  - `code === 1001 / 401` 清 token、回登录页；
  - 其他错误默认 toast，页面自渲染错误态时传 `silent: true`；
  - 分页字段不统一时在 api 层归一化，页面只消费统一结构。

## 5. 登录与店铺初始化

（若后端要求登录前带非 0 的店铺/商户标识，在此说明初始化顺序。）

```
应用启动 / 登录页
 ├─ 读取本地 merchantNo / storeId
 ├─ 缺失时调用系统配置接口并写入 store
 └─ 再执行登录 / 进入页面
```

## 6. 路由

- hash 模式，部署无需 rewrite。
- `meta.hideBottomNav`：二级页隐藏底栏。
- `meta.backTo`：顶栏返回的上级路由，支持数组。
- `meta.fullHeight`：页面自行管理底部留白。
- 旧项目路径到新路由的映射集中在 `router/legacy.js`。

## 7. 状态管理

| Store | 内容 | 持久化 |
| --- | --- | --- |
| user | token、userInfo | token 持久化，userInfo 刷新重拉 |
| config | merchantNo、storeId、storeInfo | 是 |
| 页面内状态 | 列表、分页、表单 | 否 |

购物车等高频状态如需本地优先，写入 `stores/cart.js`，不要散落在页面里。

## 8. UI 约定

- 颜色只用语义类；新增色值登记在 `assets/styles/colors.css`。
- 字体：Apple 苹方，其余平台 Noto Sans SC；数字使用 `tabular-nums`。
- 异步页面：骨架屏 + `swap` 过渡；图片：渐变占位 + 500ms 淡入 + 失败兜底。
- 顶栏统一 `PageHeader`；列表空态/错误态/加载态有统一组件。

## 9. 环境与构建

```
# .env.development / .env.production
VITE_APP_BASE_API=...
VITE_APP_TITLE=...
```

- `pnpm dev` / `pnpm build`；Node 20.19+ 或 22.12+；pnpm 9.15.9。
- 构建产物为纯静态文件，hash 路由可直接部署 nginx。

## 10. 风险与决策记录

| 事项 | 决策 | 日期 |
| --- | --- | --- |
| ... | ... | ... |
