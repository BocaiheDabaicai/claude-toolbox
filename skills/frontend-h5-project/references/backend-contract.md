# 后端契约调研与文档

> 前端迁移的第一步不是写页面，而是把后端契约搞清楚，并固化成 `docs/backend-contract.md`。接口字段以实际返回为准。

## 1. 调研顺序

1. **读旧项目请求封装**：找 `request.js` / `api/*` / `common/*`，确认：
   - baseURL、超时、请求头；
   - 成功/失败判断；
   - token 存取 key；
   - 是否全局 loading / 全局弹窗。
2. **读后端 Controller / DTO**：确认参数名、必填项、返回结构、状态枚举。
3. **看测试服实际响应**：Network / curl，记录真实字段与类型（数字/字符串/null）。
4. **看旧页面调用点**：确认哪些参数真正被使用，哪些是历史遗留。
5. **记录已知坑**：后端未校验、字段不一致、分页不统一、上传返回值等。

## 2. 文档必须包含的字段

```md
## 环境与配置
Base URL / merchantNo / storeId / 静态资源域名 / 证书说明

## 请求头
Content-Type / token / merchantNo / storeId / platform / isWechat / 经纬度

## 响应结构
{ code, message, data }，成功码、失败码、登录过期码

## 登录流程
初始化配置 → 图形验证码 → 短信验证码 → 登录 → 用户信息

## 页面接口清单
页面 / 方法 / 路径 / 关键参数 / 返回结构 / 备注

## 状态枚举
订单、支付、售后、预订单等

## 已知坑
后端未校验、字段名不一致、分页结构、上传返回值...

## 变更记录
日期 / 修改 / 依据
```

模板见 `assets/docs-templates/backend-contract.md`。

## 3. 两种常见后端形态

### 3.1 fuint clientApi

```json
{ "code": 200, "message": "操作成功", "data": {} }
```

- 成功：`code === 200`。
- 业务失败：常用 `code === 201`，`message` 可直接展示。
- 未登录/过期：`code === 1001`。
- 部分旧封装存在 `status === 5000` 的错误形态。
- 请求头通常要求：`Access-Token`、`merchantNo`、`storeId`、`platform=H5`、`isWechat`、`latitude`、`longitude`。
- 分页常见：`{ content, totalElements, totalPages }`。
- 上传：multipart 字段 `file`，返回 `{ url, filePath }`，**不是文件 ID**。

### 3.2 RuoYi

```json
{ "code": 200, "msg": "操作成功", "data": {} }
```

- 成功：`code === 200`。
- 未登录：`code === 401` 或 HTTP 401。
- 列表：`{ code, msg, rows, total }`。
- token 通常用 `Authorization: Bearer <token>`。
- 字段名是 `msg` 不是 `message`，请求层要兼容。

## 4. 登录流程模板

```
GET  system/config          → storeInfo / merchantNo（如需要）
GET  captcha/getCode        → { code: base64, uuid }
POST sms/sendVerifyCode     → 发送短信（如需要）
POST sign/signIn            → { token, userId, ... }
GET  user/info              → { userInfo, gradeInfo, ... }
```

必须记录：

- 登录前是否要求 storeId / merchantNo 非 0；
- 账号是否按 store 过滤；
- 密码是否明文提交（前端不要自行做不可逆处理）；
- 图形验证码是否区分大小写、有效期、是否消费；
- 短信验证码发送间隔与校验方式；
- 登录成功后 token / userId 的字段名。

## 5. 分页与字段归一化

后端分页常见三种：

```js
// A
{ content: [], totalElements: 100, totalPages: 10 }
// B
{ rows: [], total: 100 }
// C
{ data: { content: [], totalElements: 100 } }
```

在 api 层归一化，页面只消费一种：

```js
export async function fetchList(params) {
  const res = await getList(params)
  const data = res.data?.data || res.data || {}
  return {
    rows: data.content || data.rows || data.list || [],
    total: data.totalElements ?? data.total ?? 0,
  }
}
```

## 6. 上传

- `multipart/form-data`，字段名以接口为准（常见 `file`）。
- 前端限制类型与大小（如 jpg/png/webp，单张 ≤ 2MB）。
- 返回 `data.url` 直接用于展示/提交，不要误用文件 ID。
- 上传中显示局部 loading，失败可重试；不要复用全局 loading。

## 7. 已知坑记录模板

| # | 现象 | 原因 | 前端处理 | 后端建议 |
| --- | --- | --- | --- | --- |
| 1 | 登录提示“店铺号不能为空” | storeId=0 | 登录前初始化 config | — |
| 2 | 订单详情可看他人订单 | detail 未校验 userId | 记录风险，避免用可枚举 ID 展示敏感信息 | 增加归属校验 |
| 3 | 预订单提交不校验库存 | createPreOrder 只算价 | 前端结算前校验库存 | 建议后端补校验 |

> 后端问题不要在前端“猜着修”；记录到文档，联调时推动后端处理。

## 8. 文档维护

- 每次联调发现字段/行为与文档不一致，先修正文档，再改代码。
- 新增接口时同步更新「页面接口清单」和「状态枚举」。
- 已知坑只增不删；修复后标注修复日期。
- 不要在页面里写“后端就是这样”的魔法判断，集中到请求层/api 层。
