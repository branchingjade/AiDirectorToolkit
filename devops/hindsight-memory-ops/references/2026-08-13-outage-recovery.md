# Hindsight 停摆 22h 完整修复案例（2026-08-13）

Hermes 0.20.0 本机（Windows，uv 管理 venv）。daemon 空闲关闭后 22+ 小时不拉起，retain/recall 全停且无报错。本文是完整排查路径 + 修复命令，供同类故障对照。

## 症状

- `~/.hindsight/profiles/hermes.log` 最后一行：`Idle timeout reached (300s), shutting down daemon`（8-12 11:15），之后 0 条新记录
- `netstat` 9177 无监听、无 hindsight-api/hindsight 进程、pg0 嵌入式 postgres 未运行
- `grep "Hindsight initialized" agent.log | tail` 停在 8-12 09:16（provider 最后一次成功构造）
- `hermes memory status` 显示 Provider available（CLI 环境 OK），但 gateway 里 provider 不加载——**CLI 与 gateway 环境差异是重要线索**

## 根因链（四层）

1. **依赖丢失**：8-12 连续三次 `hermes update`，`uv pip install -e .` 失败（exit 2）→ ZIP fallback → `Optional extras failed` → hindsight 全家桶（hindsight-client/hindsight-embed/sentence_transformers/torch）被清。`update.log` 实证 `Installing dependencies: hindsight-client>=0.6.1, hindsight-all` + `Optional extras failed`
2. **uv venv shim**：`venv\Scripts\python.exe` 是 shim，真 gateway 进程 exec 到 `~/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe`（uv base python，sys.prefix=uv 目录）。判断方法：`netstat` 找 8644/8642 归属 PID → ExecutablePath 是 uv 路径；父进程是 venv shim（PPID 链）
3. **provider 静默降级**：新 gateway 里 `_check_local_runtime()` import 失败 → `is_available()`=False → agent_init 1729 块静默跳过（无日志，仅 debug）→ daemon 不再拉起
4. **pywin32 .pth**（修复依赖后仍不行的深层坑）：base python 不处理 PYTHONPATH 目录（venv site-packages）的 `.pth` → `pywin32.pth` 指向的 `win32/win32lib/pywin32_system32` 不生效 → `import pywintypes` 失败（`mcp/os/win32/utilities.py`）→ `fastmcp[server]` 的 FastMCP 不可用 → `hindsight_api/extensions/mcp.py` import 失败 → 整个 `import hindsight` 挂。**特征：venv shim 下 import 正常、uv base python 下失败**

## 修复命令（按序）

```bash
# 1. 重装依赖（先激活 venv，勿用 --python /c/ 路径——MSYS 会转坏）
source ~/AppData/Local/hermes/hermes-agent/venv/Scripts/activate
cd ~/AppData/Local/hermes/hermes-agent
uv pip install "hindsight-client==0.6.1" hindsight-all   # ~2-5min，torch 大

# 2. fastmcp server extra（hindsight MCP 扩展依赖）
uv pip install "fastmcp[server]"

# 3. sitecustomize（pywin32 .pth 修复）——写入 base python 用户 site
# 路径：C:\Users\HMSJ\AppData\Roaming\Python\Python311\site-packages\sitecustomize.py
# 内容：把 venv site-packages 的 win32、win32\lib、pywin32_system32 注入 sys.path
#       + os.add_dll_directory(pywin32_system32)

# 4. 全链验证（必须模拟 gateway 环境：PYTHONPATH 含 venv site-packages，Windows 原生路径）
PYTHONPATH='C:\Users\HMSJ\AppData\Local\hermes\hermes-agent;C:\Users\HMSJ\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages' \
VIRTUAL_ENV='C:\Users\HMSJ\AppData\Local\hermes\hermes-agent\venv' \
  "C:/Users/HMSJ/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe" -c \
  "import pywintypes; from fastmcp import FastMCP; import hindsight; from hindsight_embed import daemon_embed_manager; import sentence_transformers; print('ALL OK')"

# 5. 重启 gateway（勿用 hermes gateway CLI）
powershell "Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'gateway run' } | % { Stop-Process -Id $_.ProcessId -Force }"
powershell "Start-ScheduledTask -TaskName 'Hermes_Gateway'"

# 6. 验证修复：api_server 触发新 agent（桌面恢复会话不激活 provider，用 api 会话验证）
curl -s http://127.0.0.1:8642/v1/chat/completions \
  -H "Authorization: Bearer $(grep API_SERVER_KEY ~/AppData/Local/hermes/.env | cut -d= -f2-)" \
  -H "Content-Type: application/json" \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"ping"}],"stream":false}'
grep "Memory provider" ~/AppData/Local/hermes/logs/agent.log | tail   # 应见 activated
# daemon 拉起：netstat 9177；hermes.log 出现 migrations/retain 记录

# 7. recall 实测旧数据
curl -s -X POST http://127.0.0.1:9177/v1/default/banks/hermes/memories/recall \
  -H "Content-Type: application/json" \
  -d '{"query":"伏妖记","types":["observation"],"budget":"high","max_tokens":1024}'

# 8. daemon 保活（防再次空闲关闭断链）——config.json idle_timeout 300→0
# ~/AppData/Local/hermes/hindsight/config.json 改 "idle_timeout": 0（0=禁用自动关闭）
# 背景：daemon 空闲 300s 自动关闭后，已激活的 provider 不会自动重拉（只有新 agent 创建才拉起），
#       retain 会再次静默断链；api 会话的 keepalive 请求可临时拉起，但治本是 idle_timeout=0
```

## 排查工具速记

- **psutil 读进程环境**（拿真 gateway 的 PYTHONPATH）：`python -c "import psutil; print(psutil.Process(<pid>).environ().get('PYTHONPATH'))"`
- **MSYS 路径坑**：`PYTHONPATH=/c/...` 会被转成 `C:\c\...`（sys.path 可见）——必须 Windows 原生路径单引号包裹
- **判断 daemon 是否真活**：9177 监听 + `hermes.log` 新记录双查；pg0 postgres 惰性启动，daemon 没跑时 psql 直接 `server closed connection`
- **端口三连**：netstat 找候选 → Get-Process 验身份（8475 教训：是百度网盘 baidunetdiskhost，不是 PG）→ 再连

## 已知遗留（2026-08-13 结束时未解决）

- **桌面会话 agent 走恢复路径不激活 provider**（实测：桌面会话重建后无 `Memory provider activated`，api_server 新会话有）——桌面渠道 retain/recall 仍断，daemon 靠 api 会话的 provider 保活。待查：gateway 恢复路径（resume）为何跳过 memory 初始化
- 疑似 gateway 恢复会话与新建会话走不同 agent 创建路径；下次排查从 `gateway/run.py` 的会话恢复逻辑入手
