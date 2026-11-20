# opsctl

单台 Linux 服务器上的多项目统一启停与状态管理工具。

```bash
uv tool install .
opsctl --help
```

核心约定：

- 每个项目提供 `ops/project.toml`；
- `opsctl install` 在 `ops/systemd/` 生成 systemd 单元；
- `opsctl install --apply` 复制到 `/etc/systemd/system` 并 enable；
- `opsctl status` 同时检查 systemd、健康接口和端口；
- `opsctl start|stop|restart` 操作项目 target；
- 生产环境由 systemd 守护，`opsctl` 不常驻。

完整用法见上级目录的 `SKILL.md` 与 `references/`。
