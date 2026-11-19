# 后端接口契约

> 来源：旧项目请求封装 + 后端源码 + 测试服实际响应。
> 接口字段以实际返回为准，联调有出入时先修正本文档。

## 1. 环境与配置

| 项 | 值 |
| --- | --- |
| Base URL | ... |
| merchantNo / appId | ... |
| 默认 storeId | ... |
| 静态资源域名 | ... |
| 登录接口特殊要求 | ... |

## 2. 请求头

| Header | 值 | 说明 |
| --- | --- | --- |
| Content-Type | application/json;charset=utf-8 | 文件上传除外 |
| Authorization / Access-Token | token | 未登录传空 |
| merchantNo | ... | 缺失会查不到数据 |
| storeId | ... | 登录接口可能要求非 0 |
| platform | H5 | ... |
| isWechat | Y / N | 按 UA 判断 |
| latitude / longitude | 可空 | 定位失败静默 |

## 3. 响应结构

```json
{ "code": 200, "message": "操作成功", "data": {} }
```

| 字段/值 | 含义 | 处理 |
| --- | --- | --- |
| code 200 | 成功 | 返回响应体 |
| code 201 | 业务失败 | 默认 toast，`silent` 可跳过 |
| code 1001 / 401 | 未登录/过期 | 清 token 回登录 |
| status 5000 | 旧封装错误形态 | 按错误处理 |

分页返回常见两种：`{ content, totalElements, totalPages }` 与 `{ list, total }`，逐接口确认。

## 4. 登录流程

```
1. GET  系统配置（如需）→ 写 storeId / merchantNo
2. GET  图形验证码 → { code: base64, uuid }
3. POST 短信验证码（如需要）
4. POST 登录 → token / userId
5. GET  用户信息 → userInfo / gradeInfo
```

已知坑：
- storeId=0 导致登录失败；
- 账号按 store 过滤；
- 密码明文提交；
- token 过期码与 HTTP 401 都要处理。

## 5. 页面接口清单

| 页面/功能 | 方法 | 路径 | 关键参数 | 备注 |
| --- | --- | --- | --- | --- |
| 登录 | POST | ... | ... | ... |
| 首页 | GET | ... | ... | ... |
| 列表 | POST | ... | page / pageSize | 返回 content/totalElements |
| 详情 | GET | ... | id | ... |
| 上传 | POST | ... | multipart file | 返回 url，不是文件 ID |

## 6. 状态枚举

- 订单状态：...
- 支付状态：...
- 售后状态：...

## 7. 已知后端坑

1. ...
2. ...

## 8. 变更记录

| 日期 | 修改 | 依据 |
| --- | --- | --- |
| ... | ... | ... |
