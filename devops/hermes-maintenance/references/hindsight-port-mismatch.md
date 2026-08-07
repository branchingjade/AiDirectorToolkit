# Hindsight recall 连不上 daemon——status 全绿但端口不匹配（2026-08-07 根因）

## Symptom

`hindsight_recall` 报：

```
Failed to search memory: Cannot connect to host localhost:8888 ssl:default [远程计算机拒绝网络连接。]
```

但 `hermes memory status` 显示：

```
Provider:  hindsight
Plugin:    installed ✓   Status: available ✓   (hindsight ← active)
```

**状态全绿 ≠ 记忆可用。** `memory status` 只查插件安装与本地 runtime 导入（`is_available()`），不验证 daemon 连通性。判断 Hindsight 是否真在工作必须实测。

## Root cause：config.json 的 mode 与 daemon 实际状态脱节

`$LOCALAPPDATA/hermes/hindsight/config.json` 里 mode=`local_external` 且**没配 `api_url`** → 插件客户端默认连 `http://localhost:8888`（源码 `hermes-agent/plugins/memory/hindsight/__init__.py:57 _DEFAULT_LOCAL_URL`）。

但 daemon 实际跑在**非 8888 端口**（本机 9177）。命名 profile（hermes）不走固定 8888：`hindsight_embed/profile_manager.py` 的 `_resolve_ports` 对无显式端口/legacy metadata 的命名 profile 调 `_allocate_port`（= `8889 + sha256(profile_name) % 1000`，**hash 算出、同一 profile 名固定**——hermes → 9177，重启不变）；只有 default profile 固定 `DEFAULT_PORT=8888`。

**⚠️ 桌面设置面板 Mode 下拉框只有 Cloud / Local External，没有 local_embedded**（2026-08-07 用户实测）：面板用 `plugins/memory/hindsight/config_schema.py` 渲染，只声明两个 options；`local_embedded` 只在插件内部 schema（`__init__.py`）。UI 改不了 local_embedded——只能手改 `$LOCALAPPDATA/hermes/hindsight/config.json`；UI 可行路径 = Local External + API URL 填 `http://localhost:<实际端口>` + key 留空。

**佐证**：`$LOCALAPPDATA/hermes/logs/hindsight-embed.log` 显示 `Daemon Started (hermes @ :9177)`——这是 `local_embedded` 路径的产物（daemon 由嵌入式管理器启动），而 config 是 `local_external`，两边不一致。

## Mode 语义（决定修法）

| mode | daemon 管理 | 端口发现 | 适用 |
|---|---|---|---|
| `local_embedded` | Hermes 自动拉起/空闲关闭/再用再拉起 | 动态端口自动发现（client.url） | **推荐** |
| `local_external` | 用户/外部自行管理 | 必须手动配 `api_url`，缺省 8888 | 自管 daemon |
| `cloud` | 云端 | `api_url` 指向 api.hindsight.vectorize.io | 需 API key |

## 额外陷阱：idle_timeout

config.json 的 `idle_timeout: 300` = daemon 空闲 5 分钟自动退出。`local_external` 模式下没人拉起它 → 就算配好 api_url 也会间歇性失联。

## 诊断命令（按序）

```bash
hermes memory status                                      # 只能看插件状态，绿不代表通
cat "$LOCALAPPDATA/hermes/hindsight/config.json"          # 看 mode / api_url / idle_timeout
tail "$LOCALAPPDATA/hermes/logs/hindsight-embed.log"      # daemon 实际端口：Daemon Started (hermes @ :PORT)
netstat -ano | grep -E ":(8888|<PORT>)" | grep LISTENING   # 确认谁在听
curl -s --max-time 5 http://localhost:<PORT>/version       # 期望 {"api_version":"0.8.6",...} = daemon 健康
```

## 修复（二选一，推荐第一个）

1. config.json mode 改回 `local_embedded` —— Hermes 自动管理 daemon 生命周期 + 动态端口发现，一劳永逸
2. mode 保持 `local_external` + config.json 加 `"api_url": "http://localhost:<当前端口>"` —— daemon 需手动常驻，且 idle 5 分钟会退，不推荐

**改文件前先备份**：`cp config.json config.json.bak-$(date +%Y%m%d_%H%M%S)`。

**⚠️ 改完别再去桌面面板动 Mode 下拉框（2026-08-07 实测教训）**：面板只有 Cloud / Local External 两个选项，手改文件成 `local_embedded` 后，若用户再打开「记忆与上下文」面板并保存，配置可能被面板写回它认识的模式。明确告知用户：「面板那个下拉框不要再动了，以后改配置直接找 agent」。

## 修复后必须实测（用户会问「确认无误？」——不接受口头声称）

`memory status` 全绿不算数。**端到端验证三步**（用 venv python 模拟插件启动路径）：

```bash
cd "$LOCALAPPDATA/hermes/hermes-agent"
# 1. 静态检查：config.json JSON 有效 + mode 正确 + 本地运行时可导入
# 2. 拉起 daemon 并查 health
venv/Scripts/python.exe -c "
import os
from hindsight import HindsightEmbedded
HindsightEmbedded.__del__ = lambda self: None
client = HindsightEmbedded(
    profile='hermes',
    llm_provider='openai',
    llm_api_key=os.environ.get('HINDSIGHT_LLM_API_KEY',''),
    llm_model='deepseek-v4-flash',
    llm_base_url='https://api.deepseek.com/v1',
    idle_timeout=300,
)
client._ensure_started()
print('daemon:', client.url, '| running:', client.is_running)
"
# 3. 真读记忆（关键！证明数据库+API+数据全链路通）
venv/Scripts/python.exe -c "
import os
from hindsight import HindsightEmbedded
HindsightEmbedded.__del__ = lambda self: None
client = HindsightEmbedded(profile='hermes', llm_provider='openai',
    llm_api_key=os.environ.get('HINDSIGHT_LLM_API_KEY',''),
    llm_model='deepseek-v4-flash', llm_base_url='https://api.deepseek.com/v1', idle_timeout=300)
client._ensure_started()
res = client.memories.list(bank_id='hermes', limit=5)
print('items 数量:', len(res.items) if res.items else 0)
print(res.items[0]['text'][:80] if res.items else 'EMPTY')
"
```

`memories.list` 返回非空 items = 全链路真通（历史记忆可读出来）。

**⚠️ hindsight client API 坑（2026-08-07 实测，别走弯路）：**
- `client.recall('查询')` → `TypeError: missing positional argument`（签名不是这样）；`HindsightEmbedded.recall` 类上不存在
- `client.memories.search(...)` → `AttributeError: 'MemoriesAPI' object has no attribute 'search'`
- **正确入口是 `client.memories.list(bank_id=..., limit=...)`**——daemon 必须已 `_ensure_started()`；`client.url` / `client.is_running` 查连通与端口
- 跑完 Python 会打 `Unclosed client session` 警告——无害，是 HindsightEmbedded 的 aiohttp session 未显式 close

## 源码定位（查端口/URL 逻辑用）

- `hermes-agent/plugins/memory/hindsight/__init__.py`：`_DEFAULT_LOCAL_URL`（:57）、`_DEFAULT_API_URL`（:56）、`_get_client`、`_probe_url`、`is_available`
- `hermes-agent/venv/Lib/site-packages/hindsight_embed/profile_manager.py`：`DEFAULT_PORT=8888`（:78）、`_resolve_ports`、`_allocate_port`、`resolve_profile_paths`
- daemon 状态文件：`~/.hindsight/profiles/metadata.json`、`~/.hindsight/profiles/hermes.env`
