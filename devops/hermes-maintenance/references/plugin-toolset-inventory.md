# 插件/工具集/协议盘点档案（2026-08-14 实测快照）

本机 Hermes 能力盘点快照 + 关键协议/框架评估档案。配合 `config-audit-feature-discovery.md` 的四查框架使用。快照有时效，下次盘点时重新实测更新。

## 本机现状（审计时点 2026-08-14）

- config.yaml `plugins.enabled`：quota-panel / skill-manager / channel-sessions / ops-panel（桌面插件，不走 bundled 插件库）
- web.backend = ddgs（免 key，config 驱动——插件列表里 web-ddgs 显示 not enabled 但实际在用）
- 模型：opencode-go provider（deepseek-v4-flash），走订阅
- MCP：davinci-resolve / blender-mcp 已配但 enabled: false（MCP 铁律默认关）；eagle / ace-studio 已配

## Bundled 插件分类评估（~80 个）

| 类别 | 插件 | 评估结论 |
|---|---|---|
| 浏览器云后端 | browser-browser-use / browserbase / firecrawl | ❌ 用户浏览器铁律 = Kimi WebBridge 真实浏览器，不碰独立 profile/云浏览器 |
| Web 搜索 | web-brave-free / ddgs / exa / firecrawl / parallel / searxng / tavily / xai | ✅ web-brave-free（2k 次/月免 key，ddgs 质量兜底）；其余要 key/自建 ❌ |
| 图像生成 | deepinfra / fal / krea / openai / openai-codex / openrouter / xai | ⚠️ 用户已有本地 ComfyUI + RunningHub 管线，云端仅备胎 |
| 视频生成 | deepinfra / fal / xai | ⚠️ fal（Veo）备胎；用户主用 Seedance |
| Provider | 20+ 个（deepseek/anthropic/gemini/xiaomi/opencode-zen 等） | ❌ 当前 opencode-go 订阅覆盖，切换模型才装 |
| 平台适配器 | feishu / telegram / discord / slack / teams / whatsapp / dingtalk 等 20 个 | ❌ 用户只用飞书（且飞书走 config 非插件机制） |
| 可观测性 | langfuse / nemo_relay | ❌ 面向 Hermes 开发者 |
| 工具 | disk-cleanup / security-guidance / spotify / google_meet / teams_pipeline / a2a-platform / chronos | ✅ disk-cleanup（hooks 零维护）、security-guidance（非阻塞安全网）；⚠️ spotify（用 Spotify 才开）；❌ google_meet / teams_pipeline（飞书生态）、chronos（云端托管场景）、a2a-platform（无 peer） |
| Dashboard 认证 | basic / drain / nous / self-hosted | ⚠️ basic（scrypt 自托管密码）仅在 dashboard 暴露局域网/公网时开；drain/nous/self-hosted 面向托管多实例 |

## 工具集状态（cli 平台）

- 已启用：web / browser / terminal / file / code_execution / vision / video / image_gen / bfl / tts / skills / todo / memory / session_search / clarify / delegation / cronjob / computer_use
- 已禁用：video_gen（付费 key，bfl 免费已覆盖）/ x_search（无 X API key）/ stt（✅ 建议开：本地 faster-whisper 免费，对白转写/审听/字幕初稿实用）/ context_engine（空壳扩展点，tools 为空）/ homeassistant / spotify / yuanbao（已有 skill，工具集按需）

## A2A 插件事实（bundled：hermes-agent/plugins/platforms/a2a/）

- 入站：A2A server 默认端口 9900（A2A_PORT env 可改），发布 AgentCard
- 出站：a2a_list / a2a_orchestrate 工具
- 协议：A2A v1.0，JSON-RPC 2.0 over HTTP，纯 stdlib urllib（无 a2a-sdk 依赖）
- 鉴权：可选 bearer token，无 token 仅绑 localhost
- 评估（2026-08-14）：用户已有 delegate_task（同机并行）+ Tailscale 远程网关（9119）+ 飞书/API Server（8642）三条通道，且生态无 A2A peer → 不开，留储备（出现 A2A 兼容外部服务时再 `hermes plugins enable a2a-platform`）

## DeepSeek Harness（dsh）事实（2026-07-31 发布，2026-08-14 评估）

- 官方 GitHub：deepseek-ai/deepseek-harness，MIT
- 定位：agent harness（类 OpenClaw/Hermes），「一切皆插件」，基于 Cordis 插件系统
- 运行：`npx @deepseek-ai/dsh web`（Node.js 环境，Web UI 默认 3080 端口）
- 状态：**开发者预览**，官方 README 明示「未来将出现破坏兼容性的变更」
- 与 V4 Flash：同天发布，V4 Flash 的公开 Code Agent benchmark 测试框架就是 dsh
- 评估：竞品非 Hermes 生态；模型无关（换框架 ≠ 换模型，opencode-go 链路无绑定）；用户资产（skills/知识库/cron/飞书集成/MCP）不可迁移 → 了解即可，不迁移
