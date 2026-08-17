# Hermes 跨设备迁移提示词模板

给「新设备上的 Hermes」执行的自包含配置指令。用户在多台设备（Windows 主力机 / Mac / SteamOS / NAS）间迁移时使用。原则：**只选取跨平台通用资产，Windows 专属一律不迁**。

## 用法

1. 旧机拷贝以下文件到新设备某目录（如 `~/hermes-migrate/`）：
   - `config.yaml`、`.env`、`auth.json`
   - `memories/MEMORY.md` + `USER.md`
   - `skills/`（整目录）
   - `cron/jobs.json`（只用于列清单，不直接复制）
2. 把下方提示词粘贴给新设备上的 Hermes 执行。
3. 若目标系统是 Windows，路径改为 `C:/Users/<user>/AppData/Local/hermes/` 作源、`~/.hermes` 作目标（实际以 `hermes config path` 为准）；Linux/macOS 目标一律 `~/.hermes`。

## 提示词正文（复制此块）

```text
你是 Hermes 配置助手。任务：在 <目标系统>（Linux/macOS）上把 Hermes 配置成可用状态，配置来源=旧 Windows 机器的 Hermes 数据目录（下称「源目录」）。

【前提】源目录文件已拷贝到本机（通常 ~/hermes-migrate/，缺失时向用户确认位置；文件缺失则跳过对应步骤并告知）。

## 1. 安装
- 未安装则：curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
- 确认 ~/.hermes/ 存在（HERMES_HOME 默认 ~/.hermes）

## 2. 模型与兜底链（源 config.yaml → ~/.hermes/config.yaml）
- model.provider = opencode-go，model.default = deepseek-v4-flash
- fallback_providers = [xiaomi/mimo-v2.5-pro, xiaomi/mimo-v2.5, deepseek/deepseek-v4-flash, deepseek/deepseek-v4-pro]
- auxiliary.vision = xiaomi/mimo-v2.5
- delegation.model/provider = deepseek-v4-flash / deepseek
- approvals.mode = off（沿用旧机偏好）
- display.personality = creative
- web.backend = ddgs；装 ddgs 到 hermes venv（uv pip install --python <venv python> ddgs），验证 web search 可用
- memory.provider = hindsight（若旧机用 hindsight，配 HINDSIGHT_LLM_API_KEY）

## 3. 密钥（源 .env → ~/.hermes/.env，值不在对话中明文输出）
迁：OPENCODE_GO_API_KEY/BASE_URL、XIAOMI_API_KEY/BASE_URL、DEEPSEEK_API_KEY/BASE_URL、KIMI_CN_API_KEY/KIMI_BASE_URL、GITHUB_TOKEN、TOKENHUB_API_KEY/BASE_URL、HINDSIGHT_LLM_API_KEY、FEISHU_APP_ID/SECRET（如接飞书）
不迁：TERMINAL_*、BROWSERBASE_*、*_DEBUG、HERMES_LOCAL_STT_COMMAND、BROWSER_*（Windows 专属）
- auth.json 凭据池整体拷贝（含池化凭据）

## 4. 记忆（全量迁移）
- 源 memories/MEMORY.md + USER.md → ~/.hermes/memories/，不删条目；Windows 专属条目（NAS 地址/Clash 端口/计划任务）在新系统自然忽略

## 5. Skills（核心资产，全量迁移）
- 源 skills/ 整目录拷贝到 ~/.hermes/skills/（妖玉影视知识库、script-review、lark 系列等约 140MB）
- 拷贝后 hermes skills list 确认计数与源一致

## 6. Cron（不复制，只选取重建）
- 旧机 cron/jobs.json 内嵌 Windows 路径与飞书投递目标，直接复制必坏
- 列出任务名清单给用户，选中项用相同 schedule/prompt 重建（prompt 内脚本路径改 Linux 路径）
- 维护类 cron（备份/巡检/token 检查）按需重建

## 7. 明确不迁移（Windows 专属，别碰）
- scripts/ 下 *.ps1 / *.cmd / gateway_watchdog.py（计划任务守护）
- STT local_command（mimo_asr.py 是 Windows 本机脚本）→ 用 faster-whisper 或留空
- Clash 代理配置、Windows 路径硬编码脚本
- Hermes 源码本地补丁（hermes-local-patches.diff，飞书/Windows 专属）
- sessions/ 历史会话库（可选迁移）

## 8. 验证（全过才算完成）
1. hermes doctor 无红错
2. hermes config | grep -E "provider|model" 确认 opencode-go / deepseek-v4-flash
3. hermes chat -q "用一句话自我介绍" 链路通
4. hermes skills list | wc -l 与源一致
5. 报告：迁移了什么/跳过了什么 + 每项验证结果，诚实标注失败项
```

## 已有成功案例

- 2026-08-15 SteamOS 目标：源 = `C:/Users/HMSJ/AppData/Local/hermes/`（config.yaml/.env/auth.json/memories/skills/cron/jobs.json），用户后续通过 WebDAV 拉备份。迁移提示词按上面模板给出。
