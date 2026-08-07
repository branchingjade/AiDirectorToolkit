# Hermes 快速健康检查清单

触发场景：Hermes CLI 报错、桌面端启动失败、gateway 异常后修复验证。

## 自检步骤

按序执行，每步通过才继续：

```bash
# 1. CLI 入口可用性
hermes --version

# 2. 子 shell 继承 PATH（验证非交互环境正常）
bash -c "hermes --version"

# 3. Gateway 进程状态
hermes gateway status

# 4. 核心导入验证（排查 ImportError）
./venv/Scripts/python.exe -c "
import sys
sys.path.insert(0, r'$(pwd)')
from dotenv import load_dotenv       # 常见失败点：桌面启动
import certifi, os
assert os.path.exists(certifi.where()), 'cacert.pem missing'  # 常见失败点：TLS
from hermes_cli.main import main     # CLI 入口
print('OK: all core imports pass')
"

# 5. TLS 连通性（飞书 API 可达）
./venv/Scripts/python.exe -c "
import certifi, os, requests
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
r = requests.get('https://open.feishu.cn/open-apis/bot/v3/info', timeout=5)
print(f'OK: HTTP {r.status_code}')
"

# 6. 网关日志无新错误
tail -20 ~/AppData/Local/hermes/logs/gateway.log
tail -20 ~/AppData/Local/hermes/logs/desktop.log
```

## 陷阱

1. `hermes gateway restart` 可能超时 30s（等待飞书 WebSocket 重连），但实际重启成功——用 `status` 确认新 PID。
2. `hermes doctor` 不适合快速诊断，经常 >15s 无响应。
3. 桌面端启动失败的前 1-2 次重试可能是 venv 重建竞态窗口，看 desktop.log 确认最终成功。
