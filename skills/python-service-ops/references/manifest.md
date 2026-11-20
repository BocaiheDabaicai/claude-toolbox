# project.toml 规范

## 位置

固定放在项目根目录的 `ops/project.toml`：

```
my-project/
├─ ops/
│  └─ project.toml
├─ package.json
└─ ...
```

`project_dir` = `project.toml` 的父目录的父目录（即 `my-project/`）。`root`、`working_dir`、`env_file` 都相对它解析。

## 完整示例

```toml
[project]
slug = "crm"
name = "CRM"
type = "nuxt"                    # nuxt | vue-fastapi | custom
root = "."                       # 可选，项目根目录，相对 ops/../
env_file = ".env.production"     # 可选，相对 root
user = "deploy"                  # 可选，systemd User=
group = "deploy"                 # 可选，systemd Group=
description = "CRM 业务系统"      # 可选
after = ["postgresql.service"]   # 可选，附加 systemd After=

[project.health]
path = "/api/healthz"            # 默认 /healthz
timeout = 2                      # 秒，默认 2

[[services]]
name = "migrate"                 # 必填，小写字母/数字/中划线
kind = "node"                    # node | python | command，默认 command
command = "pnpm db:migrate"      # 必填
oneshot = true                   # 一次性任务
before = ["web"]                 # 在其他服务之前启动

[[services]]
name = "web"
kind = "node"
command = "node .output/server/index.mjs"
port = 3000                      # 可选，用于端口探测和健康 URL 推导
health = "http://127.0.0.1:3000/api/healthz"  # 可选，显式健康地址
working_dir = "."                # 可选，相对 root
systemd = "crm-web.service"      # 可选，自定义单元名，必须以 .service 结尾
restart = "on-failure"           # no | always | on-failure，默认 on-failure
restart_sec = 3                  # 默认 3
timeout_stop_sec = 15            # 默认 15
environment = { NODE_ENV = "production" }
```

## 字段说明

### [project]

| 字段 | 必填 | 说明 |
|---|---|---|
| `slug` | 是 | 项目唯一标识；只允许小写字母、数字、中划线；用于单元名和 target 名 |
| `name` | 是 | 展示名称 |
| `type` | 否 | `nuxt` / `vue-fastapi` / `custom`，仅用于标识，不影响生成逻辑 |
| `root` | 否 | 项目根目录，默认 `.`（即 `ops/` 的上级） |
| `env_file` | 否 | systemd `EnvironmentFile=`；相对 `root` |
| `user` / `group` | 否 | systemd 运行用户/组；生产环境建议显式设置 |
| `description` | 否 | 备注 |
| `after` | 否 | 额外 systemd `After=`，如 `postgresql.service` |

### [project.health]

| 字段 | 默认 | 说明 |
|---|---|---|
| `path` | `/healthz` | 服务只写 `port` 时，用此路径拼健康 URL |
| `timeout` | `2` | HTTP 健康检查超时（秒） |

### [[services]]

| 字段 | 必填 | 说明 |
|---|---|---|
| `name` | 是 | 服务名；同一项目内唯一；只允许小写字母、数字、中划线 |
| `command` | 是 | 启动命令；由 `/bin/sh -lc` 执行 |
| `kind` | 否 | `node` / `python` / `command`，仅用于标识与诊断 |
| `working_dir` | 否 | 相对 `root`；默认项目根目录 |
| `port` | 否 | 用于 TCP 探测；也是推导健康 URL 的端口 |
| `health` | 否 | 显式健康 URL，必须以 `http://` 或 `https://` 开头；不填则用 `http://127.0.0.1:<port><project.health.path>` |
| `systemd` | 否 | 自定义单元名，必须以 `.service` 结尾；默认 `<slug>-<name>.service` |
| `restart` | 否 | `no` / `always` / `on-failure`，默认 `on-failure` |
| `restart_sec` | 否 | 重启间隔，默认 `3` |
| `timeout_stop_sec` | 否 | 停止超时，默认 `15` |
| `environment` | 否 | 内联环境变量表；值会转成字符串 |
| `oneshot` | 否 | `true` 时生成 `Type=oneshot`，并强制 `Restart=no` |
| `before` | 否 | 服务名数组；本服务生成 `Before=`，被依赖服务生成 `Requires=` + `After=`；迁移失败会阻止依赖服务启动 |

## 校验规则

- `slug`、服务名必须匹配 `^[a-z0-9][a-z0-9-]*$`，防止路径和单元注入；
- 至少一个 `[[services]]`；
- 服务名不能重复；
- `before` 只能引用同项目内已存在的服务，不能引用自己；
- `systemd` 自定义名必须以 `.service` 结尾；
- `port`、`restart_sec`、`timeout_stop_sec` 为正整数；
- `oneshot = true` 时 `restart` 自动改为 `no`。

## 健康 URL 推导

优先级：

1. `service.health` 显式指定；
2. `service.port` + `project.health.path` → `http://127.0.0.1:<port><path>`；
3. 都没有 → 不做 HTTP 检查。

端口探测始终独立进行：即使健康 URL 不可达，`status` 也会显示端口是否监听。

## 路径解析

- `root`：相对 `ops/..`，即项目根目录；
- `working_dir`：相对 `root`；
- `env_file`：相对 `root`；
- 最终写入 systemd 的 `WorkingDirectory` 是绝对路径。

## 安全约定

- manifest 里不要写密码、token、cookie；
- 密钥放 `env_file`，并 `chmod 600`；
- `command` 不要包含用户输入；需要参数时用环境变量或固定脚本。
