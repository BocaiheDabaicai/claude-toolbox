---
name: python-service-ops
description: 当用户需要在单台 Linux 服务器上统一启动、停止、重启、查看多个项目运行状态，为项目生成或安装 systemd 单元，编写 ops/project.toml，或询问“所有项目是否在运行”“一键重启所有服务”“项目怎么开机自启”时使用。覆盖 opsctl CLI、manifest 规范、systemd target、健康检查、日志与故障排查；不覆盖多节点、数据库、账号管理或 Docker 编排。
version: 0.1.0
---

# 单机多项目统一运维

## 目标

用一份项目清单 + 一个 Python 控制面，在单台 Linux 服务器上统一管理多个项目的启动、停止、重启和运行状态。生产环境由 systemd 守护，`opsctl` 不常驻、不做 supervisor。

## 何时使用

- 同一台 Linux 服务器上有多个 Nuxt / Vue + FastAPI 项目；
- 需要一条命令查看所有项目是否在运行；
- 需要统一 `start` / `stop` / `restart`；
- 需要生成 systemd 单元、配置开机自启；
- 需要给项目加统一健康检查和日志入口。

## 何时不用

- 多台服务器、需要跨节点统一视图 → 需要 `ops-agent` + 中心 API，不在本 Skill 范围；
- 数据库、账号、业务数据管理 → 不在本 Skill 范围；
- Docker / Kubernetes 编排 → 用对应工具；
- Windows 生产环境 → systemd 不适用。

## 架构

```
workspace/
├─ project-a/
│  └─ ops/project.toml      # 项目清单
├─ project-b/
│  └─ ops/project.toml
└─ opsctl                   # Python CLI（控制面）

opsctl ── systemctl ── systemd ── 各项目服务
   │
   └── HTTP/TCP 健康检查、journal 日志
```

约定：

- 每个项目一个 `ops/project.toml`；
- `opsctl install` 在项目内生成 `ops/systemd/` 单元；
- `opsctl install --apply` 复制到 `/etc/systemd/system` 并 `enable`；
- 一个项目对应一个 `<slug>.target`，服务通过 `PartOf` 挂到 target；
- 状态 = systemd 状态 + 健康检查 + 端口探测。

## 标准工作流

### 0. 安装 opsctl

```bash
# 在 assets/opsctl 目录
uv tool install .
# 或
pipx install .
```

### 1. 给每个项目写 manifest

```toml
# <project>/ops/project.toml
[project]
slug = "crm"
name = "CRM"
type = "nuxt"
user = "deploy"
group = "deploy"
env_file = ".env.production"
after = ["postgresql.service"]

[project.health]
path = "/api/healthz"
timeout = 2

[[services]]
name = "migrate"
kind = "node"
command = "pnpm db:migrate"
oneshot = true
before = ["web"]

[[services]]
name = "web"
kind = "node"
command = "node .output/server/index.mjs"
port = 3000
health = "http://127.0.0.1:3000/api/healthz"
```

### 2. 自检

```bash
opsctl doctor --root /srv/projects
opsctl list --root /srv/projects
```

### 3. 生成并检查单元

```bash
opsctl render crm --root /srv/projects
opsctl install crm --root /srv/projects
```

先 review `ops/systemd/` 下的内容，再安装：

```bash
opsctl install --root /srv/projects --apply
```

非 root 时 `opsctl` 会调用 `sudo` 并提示输入密码；如果 sudo 重置 PATH 导致找不到 `opsctl`，用 `sudo "$(command -v opsctl)" install --root /srv/projects --apply`。

### 4. 日常操作

```bash
opsctl status --root /srv/projects
opsctl start crm --root /srv/projects
opsctl stop crm --root /srv/projects
opsctl restart crm --root /srv/projects
opsctl logs crm --root /srv/projects -f
```

### 5. 验收

```bash
systemctl status crm.target
opsctl status --root /srv/projects --json
sudo reboot   # 可选：验证开机自启
```

## 命令速查

| 命令 | 作用 |
|---|---|
| `opsctl list` | 发现并列出工作区项目 |
| `opsctl status [project]` | 查看 systemd、健康、端口；`--json` 给后续 UI |
| `opsctl start/stop/restart [project]` | 操作项目 target；`--service` 操作单个服务 |
| `opsctl render [project]` | 打印 systemd 单元，不落盘 |
| `opsctl install [project]` | 生成到 `ops/systemd/`；`--apply` 安装并 enable |
| `opsctl logs [project]` | 查看 journal；`-f` 跟踪，`-n` 行数 |
| `opsctl doctor` | 检查 Python、systemd、权限、manifest、目录、命令 |

全局选项：`--no-color`、`--version`；`--no-color` 放在子命令前，例如 `opsctl --no-color status`。

## 硬性规则

- 一个项目一个 manifest，路径固定为 `<project>/ops/project.toml`。
- `slug`、服务名只允许小写字母、数字、中划线；禁止路径和 shell 注入。
- 密钥只放 `env_file`，`chmod 600`；manifest 里不写明文。
- 生产环境由 systemd 守护；禁止用 `nohup`、`&` 或自定义常驻 Python 守护进程。
- `opsctl install --apply` 前必须先 review 生成的单元。
- 每个 Web/API 服务提供 `/healthz` 或等价健康接口；迁移任务用 `oneshot = true`。
- 命令通过 `/bin/sh -lc` 执行，确保登录 shell 的 PATH 能找到 `node` / `uv`，或在命令里写绝对路径。
- 本 Skill 只管“启动、停止、重启、状态”；数据库、账号、业务数据管理不属于这里。

## 质量门禁

- `uv run pytest` 通过；
- `opsctl doctor` 无 `ERROR`；
- `opsctl render` 内容人工确认；
- `opsctl install --apply` 后 `systemctl status <slug>.target` 正常；
- `start` / `stop` / `restart` 与 `status` 结果一致；
- 重启服务器后 target 能自动拉起（验证开机自启）；
- 文档中的 manifest 与实际项目一致。

## 资源索引

### references（按需加载）

- `references/manifest.md`：完整字段、校验规则、路径解析、健康 URL 推导。
- `references/systemd.md`：单元结构、target/PartOf、权限、PATH、EnvironmentFile、日志与排错。
- `references/commands.md`：CLI 全部参数、输出与 JSON 结构、退出码。
- `references/troubleshooting.md`：常见故障现象与处理。

### assets

- `assets/opsctl/`：可直接安装的 Python 包与 pytest 测试。
- `assets/examples/`：Nuxt 与 Vue + FastAPI 两份 manifest 示例。

### scripts

- `scripts/install.sh`：用 uv / pipx / pip 安装 opsctl。

## 扩展

新增能力时：

1. 通用流程/规则 → `references/`；
2. 可复制配置 → `assets/examples/`；
3. 确定性操作 → `assets/opsctl/` 并在 `SKILL.md` 登记；
4. 更新 `version` 与 `README.md` 版本记录；
5. 跑 `uv run pytest` 与一次真实工作区冒烟测试。

多节点、数据库、账号管理属于后续 `system-ops-platform` 构想，不往本 Skill 里塞。

## 不要做的事

- 不要写常驻 Python supervisor；
- 不要在 manifest 里写明文密钥；
- 不要用 `nohup` / `&` 启生产服务；
- 不要多个项目共享同一个 systemd 单元；
- 不要把数据库、账号、业务数据管理塞进本 Skill；
- 不要假设多节点——当前设计是单机工作区。
