# 字段映射

## 1. mapping.csv

```csv
target_column,source_column,target_type,required,default,transform
legacy_id,id,bigint,true,,trim
name,name,text,true,,trim
phone,phone,text,false,,digits
email,email,text,false,,lower
status,status,text,true,active,map_status
```

| 列 | 说明 |
|---|---|
| `target_column` | 目标表列名；必须已存在 |
| `source_column` | 源列名；留空表示只用 default |
| `target_type` | text / varchar / int / bigint / numeric / boolean / date / timestamptz / uuid |
| `required` | true 时空值报错 |
| `default` | 源值为空时使用；可以是常量 |
| `transform` | 内置或 `transforms.py` 中的函数名 |

## 2. 类型映射

| 源 | 目标 | 注意 |
|---|---|---|
| 字符串 ID | bigint | 确认无前导零/非数字 |
| 金额字符串 | numeric | 去千分位、货币符号；Decimal |
| `YYYY/MM/DD` | date | 用 `date` transform |
| 时间戳 | timestamptz | 确认时区；naive 默认 UTC |
| 0/1 | boolean | 用 `bool` transform |
| 状态中文 | text | 用自定义 `map_status` |
| UUID 字符串 | uuid | 用 `uuid` transform |

## 3. 内置 transform

| 名称 | 行为 |
|---|---|
| `trim` | 去首尾空格；空字符串 -> NULL |
| `lower` / `upper` | 大小写 |
| `digits` | 只保留数字（手机号） |
| `decimal` | Decimal；拒绝 NaN/Infinity |
| `bool` | 1/0、true/false、是/否 |
| `date` | ISO / `YYYY/MM/DD` / `YYYYMMDD` |
| `datetime` | ISO；naive 按 UTC |
| `uuid` | 校验并规范化 |
| `identity` | 原样 |

## 4. 自定义 transform

`transforms.py`：

```python
STATUS_MAP = {"1": "active", "0": "inactive", "正常": "active", "停用": "inactive"}

def map_status(value, row):
    if value is None:
        return "active"
    text = str(value).strip()
    return STATUS_MAP.get(text, text.lower())

TRANSFORMS = {"map_status": map_status}
```

- 函数签名 `fn(value, row)`；
- `row` 可以读取其他源字段做联合判断；
- 未知枚举不要静默丢弃：要么映射到明确值，要么报错。

## 5. ID 映射

- 优先保留旧系统业务 ID 到 `legacy_id`，目标表用新主键；
- 如果其他表引用旧 ID，需要维护 `旧 ID -> 新 ID` 映射表；
- 迁移顺序：主表 -> 子表；
- 外键列不能直接套用旧主键，除非目标主键就是旧 ID。

## 6. 状态 / 枚举

- 先画像所有取值；
- 列出映射表；
- 未知值策略：报错（推荐）或映射到 `unknown`；
- 不要 `lower()` 一把梭，除非确认所有取值。

## 7. 日期 / 时区

- 源库时区、应用时区、目标时区确认；
- naive 时间需要明确按哪个时区解释；
- 统一 `timestamptz`；
- 不要用字符串存日期。

## 8. 金额

- 目标用 `numeric`；
- Python 用 `Decimal`；
- 去掉货币符号、千分位；
- 负数、退款、精度与业务确认；
- 对账用 `sum` + 容差。

## 9. 空值 / 默认值

- `required=true` + 空值 -> 报错；
- 可选字段空字符串 -> NULL；
- 默认值只用于明确业务规则，不用于掩盖数据问题；
- 未知值不要默认成“正常”。

## 10. 映射评审清单

- [ ] 每个目标列都有来源或默认值；
- [ ] 主键/唯一键映射明确；
- [ ] 状态枚举全部覆盖；
- [ ] 日期/金额/布尔转换规则确认；
- [ ] 未知值处理确认；
- [ ] `migration-kit plan` 无 ERROR；
- [ ] 业务方签字。
