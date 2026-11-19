# MCP 配置库

集中存放 MCP Server 的配置模板、启动说明与验证方法。

## 约定

```
mcp/
├─ README.md
├─ .mcp.json.example      # 公共配置模板（可选，不含密钥）
└─ <server-name>/
   └─ README.md           # 用途、启动命令、环境变量、验证方式
```

## 安全

- 真实 token / cookie / 内部地址不要提交。
- 配置里使用环境变量占位，把真实值放在本机 `.env` 或 Claude Code 的用户级配置中。
- 如果必须提交示例，使用 `.mcp.json.example`，并在 README 中列出需要设置的环境变量。
- 对外公开仓库前，检查历史提交中是否包含过密钥；一旦泄露，先轮换密钥再清理历史。

## 使用方式

- **项目级**：在项目根目录维护 `.mcp.json`，团队共享同一套 server；含密钥时改为模板 + 本地文件。
- **用户级**：把仅自己使用的 server 配置放在本机的 Claude Code 用户配置中，不入库。
- **验证**：在 Claude Code 中查看 MCP 状态，确认 server 已连接、工具可用；具体命令以当前 Claude Code 版本为准。

## 新增 MCP 时记录

1. server 名称与用途；
2. 启动方式（npm 包 / Docker / 本地命令）；
3. 必需的环境变量与权限；
4. 最小验证步骤；
5. 已知限制与安全注意事项。
