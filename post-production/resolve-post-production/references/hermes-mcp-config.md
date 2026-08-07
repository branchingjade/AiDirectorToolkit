# Hermes MCP 配置 — davinci-resolve

## 完整配置（Hermes config.yaml）

```yaml
mcp_servers:
  davinci-resolve:
    command: "C:\\Users\\<user>\\AppData\\Local\\davinci-resolve-mcp\\venv\\Scripts\\python.exe"
    args:
      - "C:\\Users\\<user>\\AppData\\Local\\davinci-resolve-mcp\\src\\server.py"
    env:
      RESOLVE_SCRIPT_API: "C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting"
      RESOLVE_SCRIPT_LIB: "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\fusionscript.dll"
      PYTHONPATH: "C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules"
      PYTHONHOME: "C:\\Users\\<user>\\AppData\\Local\\Programs\\Python\\Python312"
    timeout: 180
    connect_timeout: 60
```

## 安装步骤

```bash
# 1. 通过 npm 一键安装
npx davinci-resolve-mcp setup --clients manual

# 2. 将打印的配置转换为 Hermes YAML 格式
# 3. 用 hermes config set 逐项写入
```

## ⚠️ 关键陷阱：hermes config set 的 args 序列化

`hermes config set "mcp_servers.X.args" '["path..."]'` 会把 args 写成字符串而非 YAML 列表：

```yaml
# ❌ 错误（hermes config set 产出）
args: '["C:\\Users\\...\\server.py"]'

# ✅ 正确
args:
  - "C:\\Users\\...\\server.py"
```

**修复方法**：用 Python 读 YAML → 手动设 `dr['args'] = [...]` → yaml.dump 写回。

```python
import yaml
with open(r'C:\Users\<user>\AppData\Local\hermes\config.yaml', 'r') as f:
    cfg = yaml.safe_load(f)
dr = cfg['mcp_servers']['davinci-resolve']
dr['args'] = [r'C:\Users\...\davinci-resolve-mcp\src\server.py']
with open(r'C:\Users\...\hermes\config.yaml', 'w') as f:
    yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
```

## 路径说明

| 组件 | Windows 路径 |
|------|-------------|
| Resolve API | `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting` |
| fusionscript.dll | `C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll` |
| Modules | `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules` |
| MCP 安装 | `C:\Users\<user>\AppData\Local\davinci-resolve-mcp` |

## 验证

```bash
# 检查 MCP 服务器可启动
C:/Users/<user>/AppData/Local/davinci-resolve-mcp/venv/Scripts/python.exe -c "
import sys; sys.path.insert(0, r'C:\Users\<user>\AppData\Local\davinci-resolve-mcp')
from src.utils.mcp_stdio import run_fastmcp_stdio
print('OK')
"
```

重启 Hermes 后，工具以 `mcp_davinci_resolve_*` 前缀出现。
