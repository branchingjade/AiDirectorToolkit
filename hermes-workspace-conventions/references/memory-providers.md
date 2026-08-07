# Hermes 外部记忆提供者（Memory Providers）对比

> 来源：Hermes 官方文档 memory-providers 页 + 本地插件源码 `plugins/memory/*/README.md`（2026-08 查询）。用户场景结论：创作内容隐私敏感 → 云端 provider 出局；本地 3 个可选。**2026-08-06 用户拍板装外部记忆插件**（session_search 平铺存档不满足"自动记住项目细节"），首选 OpenViking——详见文末「实测选型结论」。

## 总览

- 8 个外部插件：Honcho / Mem0 / Hindsight / Holographic / RetainDB / ByteRover / Supermemory / OpenViking
- **同时只能激活 1 个**，内置 MEMORY.md/USER.md 始终并行（external = additive）
- 激活后自动：注入 provider 上下文、每轮前预取相关记忆（后台非阻塞）、每轮后同步会话、会话结束提取记忆、镜像内置写入、加 provider 专用工具
- 管理：`hermes memory setup/status/off`，或 config.yaml `memory.provider: <name>`
- 关闭不影响内置记忆

## 分类

### 云端（创作内容外流风险，隐私敏感场景出局）
| Provider | 特点 | 成本 |
|---|---|---|
| Honcho | AI 跨会话用户建模+dialectic 推理+语义搜索+持久结论；5 工具 | Cloud 付费/自托管免费 |
| Mem0 | 服务端 LLM 事实提取+语义搜索+重排+自动去重；3 连接模式（Platform/自托管 Docker/OSS） | Cloud 付费/自托管免费 |
| RetainDB | 混合搜索（Vector+BM25+重排）+7 记忆类型+delta 压缩+文件工具 | $20/月 |
| Supermemory | 语义长期记忆+画像+会话图；4 工具 | Cloud 付费/自托管免费 |
| Hindsight | 知识图谱+实体解析+多策略检索；独有 hindsight_reflect 跨记忆综合 | Cloud 付费/本地嵌入式 PG 免费 |

### 本地（隐私安全）
| Provider | 特点 | 成本 |
|---|---|---|
| **Holographic** | 本地 SQLite+FTS5+信任评分+HRR 代数查询；独有 probe/reason/contradict（矛盾检测）；零依赖（NumPy 可选）；auto_extract 默认关 | 免费 |
| ByteRover | brv CLI 层级知识树+分层检索（fuzzy→LLM）；压缩前自动提取；本地默认可云同步 | 免费（本地） |
| OpenViking | **火山引擎（字节）出品**；文件系统式层级知识+L0/L1/L2 分层上下文（100t→2k→full）；自动提取 6 类记忆（画像/偏好/实体/事件/案例/模式）；需跑 server（:1933）；AGPL-3.0 | 免费 |

## 选择建议（隐私敏感场景）

1. **Holographic 最值得试**：零依赖、装完即用、`hermes memory off` 秒关；矛盾检测对创作设定管理有用；缺点默认不自动提取
2. OpenViking：字节生态亲和（豆包/火山用户），工程化最好，但 AGPL + 要跑 server，运维成本最高
3. ByteRover：最轻但能力最薄

判断标准：有"记不清上次聊到哪、FTS5 搜不到"的实际场景再引入；否则本地 MEMORY + Vault 项目库 + session_search 已是最优（隐私+零成本+可控）。

## 实测选型结论（2026-08-06，用户拍板：装外部记忆插件）

**背景**：用户要"自动记住项目进度细节（多人协作，不是一个人干活）"。session_search 只是平铺存档——不归类项目、不自动判断、不自动提取（用户三连否定"你真做到了？"）。用户明确：**"我要外部记忆插件"**。

### 五轮对比裁决（源码 + README 实证）

| 维度 | OpenViking（首选） | Holographic（备选） | ByteRover |
|---|---|---|---|
| 自动提取 | ✅ 6 类：preference/entity/event/case/pattern，会话结束自动 commit（on_session_end + atexit 兜底，源码确认） | ⚠️ auto_extract 默认关 | ⚠️ 压缩前提取，能力薄 |
| 分层上下文 | ✅ L0(~100t 摘要)/L1(~2k 要点)/L2(全文)——摘要常驻、细节按需取 | top-K 事实注入 | fuzzy→LLM 两级 |
| 隐私 | ✅ 本地 | ✅ 本地 | ✅ 本地 |
| 运维 | 🟡 常驻 server :1933（AGPL） | ✅ 零依赖零运维 | 🟡 装 brv CLI |

关键点：`event`=项目进度、`case`=决策案例、`pattern`=创作模式——恰好覆盖"项目记忆"要记的三类；L0/L1 摘要常驻解决"项目记忆太多塞不进上下文"。

### OpenViking 安装步骤（2026-08-06 已执行到 init 向导）

```bash
pip install openviking        # ⚠️ 依赖极重（scrapy/litellm/volcengine-sdk 全家桶），>300s 必须 background+长超时
openviking-server init        # 交互向导：Embedding 三选（Cloud API=VolcEngine/BytePlus/OpenAI / Local Ollama / Lightweight CPU=llama.cpp~24MB），VLM 同理
openviking-server doctor      # 校验
openviking-server             # 常驻（:1933），可配自启
hermes memory setup           # 选 openviking 激活
# ~/.hermes/.env: OPENVIKING_ENDPOINT=http://127.0.0.1:1933
# 版本要求 0.2.10+（0.2.6 及更早 deprecated）
```

### ⚠️ PYTHONPATH 污染坑（Windows + Hermes shell 跑全局 CLI）

症状：全局 Python312 跑 `openviking-server` 报 `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'`——全局解释器加载了 Hermes venv 的 site-packages（pydantic 版本不匹配）。

根因：Hermes 会话 shell 的 `PYTHONPATH` 指向 `hermes-agent` + `venv\Lib\site-packages`，`which python` 也解析到 venv——任何全局 pip 装的 CLI 从 Hermes shell 启动都会被污染。

修复：`unset PYTHONPATH` 后用**全局解释器绝对路径**显式跑（`/c/Users/HMSJ/AppData/Local/Programs/Python/Python312/Scripts/openviking-server`）。凡是"全局装的 Python CLI 在 Hermes shell 报 pydantic/模块缺失"先查 PYTHONPATH，别急着重装。

### ⚠️ 装包事故 + 卸载结局（2026-08-06 实测，最终定稿）

**事故**：`pip install openviking` 从 Hermes shell 跑（PYTHONPATH 污染状态下），pip 误把 venv 当目标环境——venv 内 `cryptography` 核心文件丢失（`hashes.py` 被撕）、`charset_normalizer` 损坏、`pip` 模块消失，`hermes` 命令启动崩溃（`ImportError: cannot import name 'hashes'`）。**修复**：`venv/Scripts/python.exe -m ensurepip` 恢复 pip → `--force-reinstall cryptography` → `--force-reinstall charset_normalizer`。

**MiMo 不能做 embedding（实测）**：`GET /v1/embeddings` 返回 404；模型列表只有 mimo-v2.5/-asr/-tts 系列，无 embedding 模型。OpenViking 的 embedding 配置支持 `provider: openai` + 自定义 api_base（任何 OpenAI-compatible 端点可接），但 MiMo 没有 embedding 端点——embedding 须另选（Ollama/llama.cpp CPU/火山 embedding API）；MiMo 只能当 VLM（mimo-v2.5 有 vision）。

**结局（第一轮）**：用户拍板"卸载吧"——外部记忆插件的收益 < 环境破坏风险，就此打住。**回归原点**：session_search（存档）+ 全局 MEMORY（注入）+ Obsidian（git 归档）。诚实承认：Hermes 无项目级自动记忆，三者都不是项目级——不包装、不夸大。⚠️ **当日稍后反转**：用户主动重跑 `hermes memory setup` 要求全量对比 8 provider，改选 **Hindsight 本地嵌入式**并安装成功——见文末「二次安装定稿」。

### 二次安装定稿（2026-08-06 当日，Hindsight 本地嵌入式，安装成功 ✅）

用户反悔后重跑 `hermes memory setup`，要求**全量对比 8 provider**（对比表按 部署/自动提取/检索注入/运维/费用 五维，附官方文档+本地 README 实证）→ 拍板 **Hindsight local_embedded**。

**为什么是 Hindsight**：自动提取 ✅（会话结束保留）+ 本地隐私 ✅ + 知识图谱/实体解析能力最强 + **daemon 自动起停无需常驻**（5 分钟空闲自动停）——比 OpenViking 轻（无 200MB+ 全家桶、无 PYTHONPATH 事故风险）、比 Holographic 强（auto_extract 默认开）。只需 1 个 LLM API key（OpenAI-compatible 即可）。

**⚠️ 关键坑：`hermes memory setup` 向导是 curses 全屏 UI**（方向键+Enter），后台 PTY `submit` 行输入驱动不了 → 进程卡死无输出。**绕过法：手动配置**（README 支持）：

1. **装依赖**（用 venv 直连，勿从 Hermes shell 裸 pip——PYTHONPATH 污染教训见上）：
   ```bash
   cd ~/AppData/Local/hermes/hermes-agent && venv/Scripts/python.exe -m pip install "hindsight-all>=0.6.1"
   # ~400MB（torch/sentence-transformers/嵌入式 PG pg0-embedded 全家桶），必须 background+notify_on_complete
   ```
2. **写 `$HERMES_HOME/hindsight/config.json`**（mode=local_embedded + openai_compatible）：
   ```json
   {
     "mode": "local_embedded",
     "llm_provider": "openai_compatible",
     "llm_base_url": "https://api.deepseek.com/v1",
     "llm_model": "deepseek-v4-flash",
     "bank_id": "hermes",
     "recall_budget": "mid",
     "memory_mode": "hybrid",
     "timeout": 120,
     "idle_timeout": 300,
     "auto_recall": true,
     "auto_retain": true,
     "retain_every_n_turns": 1
   }
   ```
   注意：daemon 内部把 `openai_compatible`/`openrouter` 映射为 `openai` wire format（源码 `_build_embedded_profile_env`），DeepSeek 无预设 provider 但走 openai_compatible 完全兼容。
3. **`.env` 追加 `HINDSIGHT_LLM_API_KEY=<复用 DEEPSEEK_API_KEY>`**（hindsight 读 `get_secret("HINDSIGHT_LLM_API_KEY")`，不认 DEEPSEEK 变量名，必须单独写）。
4. **config.yaml**：`memory.provider: hindsight`。
5. 验证：`hermes memory status` → `Provider: hindsight` + `Plugin: installed ✓` + `Status: available ✓`。

**DeepSeek 实测**：`GET /v1/models` 返回 `deepseek-v4-flash`/`deepseek-v4-pro`（2026-08），API key 在 `~/AppData/Local/hermes/.env`（不是 `~/.hermes/.env`——本机 HERMES_HOME 是 AppData 路径，`~/.hermes/.env` 只有 28 行壳，真实凭据在 475 行的 `~/AppData/Local/hermes/.env`，凭据池 auth.json 同目录）。MiMo 无 embedding（404 实测）不影响 Hindsight——embedding 走本地 sentence-transformers（首次 daemon 启动下载模型会慢），LLM 仅用于提取/综合。

**E2E 实测（2026-08-07 跑通 ✅）**：daemon 启动成功（嵌入式 PG + pgvector 迁移，:9177）；`handle_tool_call('hindsight_retain', {...})` 存入 → daemon 异步 consolidation 用 DeepSeek LLM 提取（8.6s/条，created=1）→ `handle_tool_call('hindsight_recall', {'query': ...})` 语义检索返回正确记忆。注意：provider 方法名不是 retain()/recall()，是 `handle_tool_call` + 工具名 `hindsight_retain`/`hindsight_recall`；retain 是异步的（retain_async=true），存完立即 recall 会查不到，需等 consolidation 完成（~10s）；daemon 子进程 stderr 有非 UTF-8 字节（UnicodeDecodeError 噪音，不影响功能）。`hermes update` 重建 venv 会清掉 hindsight-all 需重装（同 read_file 补丁风险）；新会话才激活（"Start a new session to activate"）。daemon 日志：`~/.hermes/logs/hindsight-embed.log`。

### ⚠️ daemon 空闲自动停止坑（2026-08-07 实测：retain 长期静默失效）

local_embedded 的 daemon 有 `idle_timeout=300`（**5 分钟无请求自动停止**，这是安装定稿里"自动起停无需常驻"特性的代价）。provider 只在 agent `initialize()` 时启动 daemon（`_start_daemon` 线程 → `client._ensure_started()`）；**daemon 空闲退出后，后续 retain/recall 全部失败**——`_run_hindsight_operation` 的"重试一次"逻辑只重建 client 对象，不重启 daemon 进程（源码 `plugins/memory/hindsight/__init__.py` ~line 1400）。

- **症状链**：`netstat -ano | grep 9177` 无监听（daemon 已退出）→ agent.log 反复报 `ConnectionRefusedError: [WinError 1225] 远程计算机拒绝网络连接`（traceback 走 hindsight_client aretain_batch/arecall）→ hindsight-embed.log 最后一条还是成功的「Daemon Started (hermes @ :9177)」。**E2E 实测当天 16:58 daemon 启动成功，17:04 已因空闲退出导致 recall 被拒**——"自动起停"是双刃剑：长时间不用后第一个请求必然失败（或触发慢速重建）。
- **诊断结论不可只看 `hermes memory status`**：它只报 provider 配置可用（available ✓），**不证明 daemon 在跑**。判断 Hindsight 是否真在工作：① netstat 查 9177 监听 ② agent.log 无 ConnectionRefusedError。症状=记忆实际存不进去，但 agent 侧无感。
- **修复方向（未实测）**：`idle_timeout: 0` 禁用自动停止（daemon 常驻，代价内存 ~1GB）；或高频使用让它不空闲；飞书/桌面混合使用场景下 5 分钟窗口极易触发。
- **多用户隔离注意**：bank_id 固定 `"hermes"`（未配 bank_id_template）时，**所有渠道/所有用户共享一个 bank**——多人飞书协作若需按人隔离，配 `bank_id_template`（占位符 `{profile}/{workspace}/{platform}/{user}/{session}`，见 `_resolve_bank_id_template`，如 `hermes-{platform}-{user}`）。
- **provider 激活是全局的**：`agent_init.py` 统一初始化（所有渠道桌面/飞书/评论/cron 共用 config.yaml `memory.provider`）——飞书 agent 同样激活 Hindsight，"飞书记忆"其实已在 Hindsight 覆盖范围内，无需另建。

### 核查命令

- `hermes memory status` — 内置/外部 provider 状态（本机 7 个已装，supermemory 需 API key 未装）
- `hermes memory off` — 关闭外部（内置不受影响）；同时只能激活 1 个 provider

### 教训（对 agent）

用户要"自动记住项目细节"时，**不要自建 Obsidian 记忆层**（项目记忆.md/台账/cron 盘点全被否——"怎么全要我自己搞"）；也不要把 session_search 吹成"已经做到了"（"你真做到了？"被三连打脸）。诚实路径：内置能力（session_search 存档 + MEMORY 全局注入）讲清楚 → 用户要更强时指向 **Hermes 原生的外部记忆插件**（`hermes memory setup`），选型按隐私→自动提取→分层→运维排序。
