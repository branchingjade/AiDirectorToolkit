# DaVinci Resolve MCP 配置参考

## 当前版本
- MCP: v2.62.1 (2026-07 更新)
- Resolve: 21.0.2.4 Studio

## 更新方法
1. `git clone --depth 1 https://github.com/samuelgursky/davinci-resolve-mcp.git <new-dir>`
2. `python -m venv venv && venv/Scripts/pip install -r requirements.txt anyio mcp`
3. 更新 `config.yaml` 中 `mcp_servers.davinci-resolve.command` 和 `args[0]`
4. 确保 PYTHONHOME 与 venv Python 版本一致
5. 重启 Hermes

## 踩坑
- `hermes config set args[0]` 有序列化 bug，需 Python + yaml.dump 直接编辑
- PYTHONHOME 版本不匹配会导致 import 失败
- 旧目录被进程占用时需 kill 进程或重启后清理
