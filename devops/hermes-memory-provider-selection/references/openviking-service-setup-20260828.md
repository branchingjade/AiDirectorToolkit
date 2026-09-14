# OpenViking Service 模式接入实测 (2026-08-28)

**端到端本机验证**:用户切换 provider 从 Hindsight 到 OpenViking 的真实流程。结论: **Service 模式直连失败**,需要降级到 self-hosted 或继续 debug 鉴权。

## 1. 决策触发

用户原话: "hermes memory setup openviking" + 后续 "火山引擎服务" (走 OpenViking Service 云服务)。

skill `hermes-memory-provider-selection` 的决策框架: 三个触发信号(质量问题/商业化/token 账单)没触发,**严格说本不该换**——但用户已经拍板"切过去",所以执行。

## 2. 关键事实(2026-08-28 本机实测)

| 维度 | 事实 |
|---|---|
| 内置 provider | `hermes-agent/plugins/memory/openviking/` (v2.0.0) — Hermes 已带,无需安装 |
| config 当前值 | `config.yaml` 里 `memory.provider: openviking` 已存在 (这次切之前就有,说明此前错配) |
| `openviking` pip 包 | 0.4.16 (≥0.2.10 要求满足) |
| `openviking-sdk` | 0.1.9 (真实 SDK 在这) |
| `openviking_cli` | thin wrapper,真正实现走 `_http_compat.py` |
| Service endpoint | `https://api.vikingdb.cn-beijing.volces.com/openviking` (插件源码硬编码) |
| 鉴权 headers | `Authorization: Bearer <ak>` + `X-Account-Id` + `X-User-Id` |
| 默认 account/user/agent | `default`/`default`/`hermes` |

## 3. venv 装包(本机硬性约束)

**Hermes 跑在 venv 里,系统 pip 装的包 Hermes 看不到**:

```bash
# venv 在: C:\Users\HMSJ\AppData\Local\hermes\hermes-agent\venv\
# venv 只有 pip3.exe (没有 pip.exe)
'/c/Users/HMSJ/AppData/Local/hermes/hermes-agent/venv/Scripts/pip3.exe' install openviking
```

`pip install openviking` 直接装会装到 `C:\Users\HMSJ\AppData\Local\Programs\Python\Python312\Lib\site-packages`(系统 Python),`import openviking` 在 hermes venv 里 `ModuleNotFoundError`。

## 4. SDK 调用现象

| 调用 | 返回 | 解读 |
|---|---|---|
| `SyncHTTPClient.health()` | `False` (200 但 body=`false`) | 不是真健康检查,默认占位返回值 |
| `SyncHTTPClient.find(query="*")` | `RuntimeError: Client is not initialized` | SDK 生命周期要先 `initialize()` |
| `SyncHTTPClient.ls("viking://user/")` | 同上 | 同上 |
| `SyncHTTPClient.get_status()` | 同上 | 同上 |

## 5. 裸 HTTP 直连 Service (失败现场)

```python
import httpx
ep = "https://api.vikingdb.cn-beijing.volces.com/openviking"
h = {"Authorization": f"Bearer {ak}", "X-Account-Id": "default", "X-User-Id": "default"}

httpx.get(f"{ep}/health", headers=h)
# → 401 {"code":"AuthenticationError","message":"The API key in the request is missing or invalid..."}

httpx.get(f"{ep}/api/v1/system/status", headers=h)
# → 401 同上

httpx.post(f"{ep}/api/v1/fs/ls", headers=h, json={"uri": "viking://user/"})
# → 404 (路径前缀不对 — 可能 `viking` 前缀或别的)
```

**根因推测**: Service 端可能走火山 IAM 完整签名 (HMAC-SHA256 + `X-Date` 等 header),不是 Bearer。Self-hosted `openviking-server` 走另一套鉴权 (`root_api_key` 或 dev 模式无鉴权)。

## 6. API key 格式

64 字符 hex 字符串 (类似 SHA256) — 不是火山 IAM 传统的 `AK...` 形式。来源是火山控制台 OpenViking Service → "API Key 管理"页。

## 7. 安全写入流程 (Hermes 输出流会 mask `sk-` 等敏感前缀)

- 不要用 `cat | grep` 验证写入,会被 mask 成 `***`(stdout 触发)
- 用 `python open(r"C:\...\file").read()` 读 + re 校验长度
- 写入走 Python re.sub 替换 `__FILL_HERE__` 占位符,不要 echo

## 8. 备份归档铁律

切 provider 前必须备份:
- `config.yaml`
- `.env` (含 `HINDSIGHT_LLM_API_KEY`)
- 当前 provider 的 `plugin.yaml`

归档路径示例: `scripts/_archive/<日期>-<主题>/`。git 自动 rename 保留历史。

## 9. 回滚(还没切完就要回滚时)

```yaml
# config.yaml
memory:
  provider: hindsight    # 改回
```

`.env` 里 `HINDSIGHT_LLM_API_KEY` 没动(已备份确认),provider 一改回就生效。

## 10. 待办(用户回来后继续)

- [ ] 选 A: 重新从火山控制台拿正确的 OpenViking Service key (注意 IAM 权限/激活状态)
- [ ] 选 B: 切 self-hosted `openviking-server` (port 1933, 本机起 server, 无鉴权或 root_api_key)
- [ ] 选 C: 暂停,我查官方对接流程

## 11. 备份文件位置

`scripts/_archive/2026-08-28-openviking-switch/`:
- `config.yaml.before-hindsight` (原始 config)
- `env.before-hindsight` (原始 .env)
- `env.before-hindsight.live` (上一份 .env)
- `hindsight-plugin.yaml` (hindsight plugin 快照)
- `snapshot.md` (本次决策记录)