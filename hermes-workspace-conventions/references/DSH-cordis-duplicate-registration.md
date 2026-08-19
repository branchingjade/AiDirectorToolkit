# DSH 启动失败：cordis 双重注册（Service already registered）

> 2026-08-19 实测。DSH web 启动后 session.create 立刻报 `agent-preset-invalid`，
> 桥包错 `session-not-found`——根因在 cordis Service 注册冲突，不是 prompt 参数问题。

## 现象

DSH web UI 正常加载（127.0.0.1:8080 返回 HTML），但 session.create 失败：

```json
{"code": "agent-preset-invalid",
 "message": "agent-presets: preset \"creator\" failed to mount:
  failed to apply loader entry tool-cordis (@deepseek-ai/dsh-tool-cordis):
  Host Cordis inspect provider \"Service\" is already registered
  (C:\\Users\\HMSJ\\.dsh\\.agent-presets\\creator\\agent.cordis.yml)",
 ...}
```

**桥表现为**：`session.prompt: 'session "hermes-xxx" not found'`——
session 没真正建好，后续 prompt 当然 404。

## 根因（实测挖到）

**双重注册 `skill-filesystem` 的 23 个分类目录**：

- `~/.dsh/.agent-presets/creator/agent.cordis.yml` 第 255-292 行（preset 级）
- `~/.dsh/cordis.patch.yml` 第 8-31 行（机器级 home patch）

两份都列出 `C:/Users/HMSJ/.dsh/skills/devops`、`.../creative`、`.../妖玉影视` 等
23 个 customSkillDirs。DSH 启动时两层都执行 skill-filesystem，每个 skill 在
cordis Service 注册表里报 "already registered" → preset 挂载失败 → session.create
连带失败。

## 修复

**只保留机器级（`cordis.patch.yml`），删除 preset 层的 23 行**：

```yaml
# ~/.dsh/.agent-presets/creator/agent.cordis.yml  (修复后)
- id: skill-filesystem
  name: '@deepseek-ai/dsh-skill-filesystem'
  config:
    customSkillDirs:
      # 只需 preset 自带的技能目录（cordis-plugin-development、editing-cordis-compositions）
      - !!js "process.getBuiltinModule('node:url').fileURLToPath(new URL('skills/', baseUrl))"
      # 分类子目录的扫描由 ~/.dsh/cordis.patch.yml（机器级）统一负责，preset 层不再重复注册，
      # 否则 cordis Service provider key 会报 "already registered"。

- id: tool-skill
  name: '@deepseek-ai/dsh-tool-skill'
```

**同样要修 `~/.dsh/.agent-presets/hermes-cordis/agent.cordis.yml`**——它和 creator
是别名（"Hermes 创造模式"），共用同一份配置。

## 验证（按顺序）

```bash
# 1. 重启 DSH web（计划任务或手动）
netstat -ano | grep ':8080' | grep LISTENING   # 监听在
curl - -X POST http://127.0.0.1:8080/api/session.create \
  -H 'content-type: application/json' \
  -d '{"type":"client-request","rpcId":"r1","method":"session.create",
       "payload":{"sessionId":"verify-cordis-fix-001",
                  "cwd":"C:/Users/HMSJ/Documents/Hermes"}}'
# 期望：{"result":{"ok":true,"value":{"sessionId":"verify-cordis-fix-001",
#                                       "agentPreset":"creator"}}}

# 2. 端到端走桥
python scripts/dsh_bridge.py run "C:/Users/HMSJ/Documents/Hermes" \
  "hello" --route cordis-fix-verify
# 期望：DSH 回 "hello"，回合结束，BRIDGE_RESULT.status=done
```

## 复发风险

⚠️ **DSH 升级会覆盖 `~/.dsh/.agent-presets/` 整个目录**（包括手动修复的
agent.cordis.yml）——下次升级前要先备份修改后的 yml，升级后比对还原。
脚本路径：
- `C:\Users\HMSJ\.dsh\.agent-presets\creator\agent.cordis.yml`
- `C:\Users\HMSJ\.dsh\.agent-presets\hermes-cordis\agent.cordis.yml`

## 相关决策

DSH 侧 preset 配置文件**不在 Hermes 工作区 git 追踪**（属于 DSH 自己的资产，
按 2026-08-19 拆墙决定两侧解耦）——因此本修复无法 commit 到 Hermes 仓库。
只能靠 DSH 升级后手动 reapply，或在 `.hermes/` 下加个"DSH preset 补丁清单"
文件记录差异，升级后照单恢复。

## 顺手的次要发现

修复 cordis bug 期间发现的几件配套事：

1. **DSH web 启动慢**：首次启动需 20-40 秒加载 skills/storages（取决于磁盘），
   启动后立刻调 session.create 可能还在 boot 中段——给 DSH 30 秒热身。
2. **session.create 必须带 cwd 或 workspaceId**：裸调 `{"sessionId":"x"}`
   不报错但 workspace 不会归类，session 会落到 web UI 的"未分组"分类（不影响功能）。
3. **正确信封格式**：DSH /api 网关期望 `{"type":"client-request", "rpcId":..., "method":..., "payload":...}`——桥 `rpc()` 函数已封装，agent 不要裸 curl。