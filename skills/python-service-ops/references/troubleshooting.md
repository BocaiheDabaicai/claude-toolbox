# 常见问题

## opsctl 找不到项目

现象：

```
错误: 在 /srv/projects 下没有找到任何 ops/project.toml
```

检查：

1. 路径是否为 `<project>/ops/project.toml`；
2. `--root` 是否指向项目们的父目录；
3. manifest 是否因为字段错误被跳过（`list` 会打印警告）。

```bash
opsctl doctor --root /srv/projects
```

## systemd 单元 not-found

现象：

```
SYSTEMD
not-found
```

原因：

- 还没执行 `install --apply`；
- 执行了但没 `daemon-reload`（`--apply` 会自动做）；
- 单元名与 manifest 不一致。

```bash
opsctl install --root /srv/projects --apply
systemctl cat crm-web.service
```

非 root 时 `opsctl` 会内部调用 `sudo`；如果 sudo 重置 PATH 找不到它，用 `sudo "$(command -v opsctl)" ...`。

## 服务起不来，状态 failed

```bash
systemctl status crm-web.service
journalctl -u crm-web.service -n 200 --no-pager
```

常见 systemd 退出码：

| 退出码 | 原因 | 处理 |
|---|---|---|
| `203/EXEC` | 命令找不到 | 用绝对路径或修正 PATH |
| `200/CHDIR` | 工作目录不存在 | 检查 `root` / `working_dir` |
| `217/USER` | 运行用户不存在 | 检查 `user` / `group` |
| `1` | 应用自身报错 | 看应用日志与 `.env` |

## 命令在终端能跑，systemd 跑不了

systemd 不读 `.bashrc`。检查：

1. 命令是否在 `/usr/bin`、`/usr/local/bin`；
2. nvm / uv / pnpm 是否只在交互式 shell 的 PATH；
3. 用绝对路径，或设置：

```toml
environment = { PATH = "/usr/local/bin:/usr/bin:/bin" }
```

## 健康检查失败，但 systemd 是 active

可能原因：

- 应用只监听 `127.0.0.1`，健康 URL 写错端口；
- 应用启动慢，超过 `timeout`；
- HTTPS 自签证书导致 `urllib` 校验失败（健康检查建议用 HTTP 内网地址）；
- 健康路径不存在，返回 404。

```bash
curl -i http://127.0.0.1:3000/healthz
```

## 端口关闭，但 systemd 是 active

- 应用启动后崩溃，systemd 可能正在重启；
- 应用监听的端口与 manifest 不一致；
- 端口被其他进程占用。

```bash
ss -lntp | grep 3000
journalctl -u crm-web.service -n 100 --no-pager
```

## 权限不足

```
需要 root 权限，且找不到 sudo
```

- `opsctl` 在非 root 时会自动调用 `sudo`；
- 如果 sudo 重置 PATH 找不到 `opsctl`，用 `sudo "$(command -v opsctl)" ...`；
- 或给部署用户配置最小 sudoers，只允许操作本项目的 target 与 service；
- `status` / `list` / `render` 不需要 root。

## 开机没有自启

```bash
systemctl is-enabled crm.target
```

如果 `disabled`：

```bash
sudo systemctl enable crm.target
```

`opsctl install --apply` 会自动 enable，但如果你手动复制了单元，需要自己 enable。

## 修改了 manifest，但行为没变

`opsctl install` 只生成文件；`--apply` 才会更新系统单元并 `daemon-reload`。

```bash
opsctl install crm --root /srv/projects
opsctl install crm --root /srv/projects --apply
sudo systemctl restart crm.target
```

## 中文输出乱码

Windows 控制台代码页可能不是 UTF-8。`opsctl` 已尝试把 stdout/stderr 重设为 UTF-8；如果仍乱码：

```bash
chcp 65001
```

生产 Linux 通常默认 UTF-8，不受影响。

## status 很慢

- 每个服务有端口探测和 HTTP 健康检查超时；
- 端口关闭时会跳过 HTTP 检查；
- 服务较多时并行检查（最多 8 个）；
- 如果仍然慢，检查网络/防火墙是否让 TCP 连接挂起。
