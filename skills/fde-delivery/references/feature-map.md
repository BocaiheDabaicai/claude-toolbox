# 业务功能点地图与台账

## 1. 能力地图

先按业务能力分层，不按页面：

```
客户管理
├─ 客户资料
├─ 客户状态
└─ 客户导入
订单管理
├─ 下单
├─ 支付
└─ 售后
报表
├─ 客户增长
└─ 订单汇总
```

能力地图用于发现遗漏；功能点台账用于执行。

## 2. 功能点台账

`docs/features.csv`：

```csv
id,module,feature,description,priority,status,owner,acceptance,dependencies,notes,updated
F-001,登录,管理员登录,邮箱+密码,P0,accepted,张三,正确账号可登录；错误不泄露账号是否存在,,,2026-11-20
```

| 字段 | 说明 |
|---|---|
| id | `F-001`，只增不改 |
| module | 业务模块 |
| feature | 功能点名称 |
| description | 一句话说明 |
| priority | P0/P1/P2 |
| status | 状态机 |
| owner | 负责人；进行中/验收必须有 |
| acceptance | 可验证的验收标准 |
| dependencies | 依赖的功能 ID，用 `;` 分隔 |
| notes | 风险、原因、链接 |
| updated | 最后更新日期 |

## 3. 状态

```
idea -> scoped -> in-progress -> demo -> accepted
         |             |
         +-> blocked <-+
         +-> deferred / cut
```

- `idea`：想法，未确认；
- `scoped`：范围/验收已确认；
- `in-progress`：开发中，必须有 owner；
- `blocked`：阻塞，必须有 owner 和 notes；
- `demo`：可演示，待验收；
- `accepted`：验收通过，必须有 owner + acceptance；
- `deferred`：暂缓，notes 写原因；
- `cut`：砍掉，notes 写原因。

## 4. ID 与优先级

- ID 只增不改，删除功能点也保留 ID（状态改 `cut`）；
- P0：不做就无法交付/无法验收；
- P1：本期应该做，可协商；
- P2：锦上添花，可延期；
- 不要把超过 30% 的功能点标 P0。

## 5. 验收标准

好的 acceptance：

- “正确账号可登录；错误提示不泄露账号是否存在”；
- “搜索/分页/空态正常；软删客户不出现”；
- “导入成功后行数与源文件一致；失败行可下载重试”。

不好的：

- “登录正常”；
- “体验好”；
- “和原来一样”。

写法：

- 一条功能点 1–3 条可验证标准；
- 能用测试/截图/对账证明；
- 复杂验收放 `acceptance.md`。

## 6. 依赖

- `F-003` 依赖 `F-002`：先做列表再做编辑；
- 循环依赖说明切片设计有问题；
- 外部依赖（接口、数据、权限）写 notes；
- `feature_lint` 会检查依赖存在和自依赖。

## 7. 追踪

一个功能点至少能追到：

- 页面/路由；
- 接口；
- 表/字段；
- 测试/验收证据。

可以在 notes 放链接，不要复制整张表。

## 8. 校验

```bash
python scripts/feature_lint.py docs/features.csv
python scripts/feature_lint.py docs/features.csv --strict
```

检查：

- ID 格式/重复；
- 必填字段；
- 状态/优先级；
- owner/acceptance；
- 依赖存在；
- 汇总。
