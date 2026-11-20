# python-service-ops

单台 Linux 服务器上的多项目统一启动、停止、重启与运行状态管理 Skill。

## 它解决什么

同一台服务器上有多个 Nuxt / Vue + FastAPI 项目时，分别登录、找目录、记启动命令、检查端口很低效。这个 Skill 用一份 `ops/project.toml` 清单和一个 `opsctl` CLI，把“发现项目、生成 systemd 单元、启停、看状态、看日志”统一起来。

生产环境由 systemd 守护，`opsctl` 只是控制面，不常驻。

## 快速使用

```bash
# 1. 安装
cd assets/opsctl
uv tool install .

# 2. 给项目写 ops/project.toml
#    可参考 assets/examples/nuxt.project.toml

# 3. 检查
opsctl doctor --root /srv/projects
opsctl list --root /srv/projects

# 4. 生成并检查单元
opsctl install crm --root /srv/projects
opsctl render crm --root /srv/projects

# 5. 安装并启用（非 root 时 opsctl 会调用 sudo）
opsctl install --root /srv/projects --apply

# 6. 日常
opsctl status --root /srv/projects
opsctl start crm --root /srv/projects
opsctl stop crm --root /srv/projects
opsctl restart crm --root /srv/projects
opsctl logs crm --root /srv/projects -f
```

## 目录

```
python-service-ops/
├─ SKILL.md                 # 触发条件、流程、硬性规则
├─ README.md                # 本文件
├─ references/              # manifest、systemd、命令、排错
├─ assets/
│  ├─ opsctl/               # Python 包（含 pytest）
│  └─ examples/             # Nuxt / Vue+FastAPI manifest 示例
└─ scripts/
   └─ install.sh            # 安装脚本
```

## 开发与测试

```bash
cd assets/opsctl
uv sync
uv run pytest
uv run opsctl --help
```

## 版本记录

| 版本 | 日期 | 内容 |
| --- | --- | --- |
| 0.1.0 | 2026-11-20 | 初始版本：manifest、systemd target、list/status/start/stop/restart/install/render/logs/doctor、JSON 输出与测试 |
