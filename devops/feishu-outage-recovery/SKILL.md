---
name: feishu-outage-recovery
description: "Use when 飞书不回消息/宕机/API挂掉: 查gateway→重启→拉停机窗口消息→批量补回复。"
version: 1.0.0
tags: [feishu, gateway, outage, recovery, troubleshooting]
---

# 飞书宕机/API 挂掉排查与停机消息恢复

当飞书 bot 不回消息、gateway 疑似宕机、或 API 大面积失败时，按此流程走。2026-08-07 实战验证（gateway 10:56 停机 3.5h，4 人 18 条消息未回复，全部补回）。

## 一、判定宕机与定位窗口

1. **看 gateway 是否活着**：
   ```bash
   tail -20 ~/AppData/Local/hermes/logs/gateway.log
   ps aux | grep -i "gateway\|hermes" | grep -v grep
   ```
   **铁证**：日志末尾出现 `Gateway stopped` / `Shutdown phase` = gateway 已停。记录停机时间点（日志里 `Sending shutdown notification` 或 `Gateway stopped` 的时间）。
   注意：停机瞬间若 `drain: active_at_start=0` 说明无正在处理的会话（无任务被中断，只是消息没人接）。

2. **确认恢复机制是否触发**：`grep -i "resum\|suspend" gateway.log | tail`——`resume_pending` 全 False + 无 `Scheduled auto-resume` 日志 = 停机窗口没有可恢复会话（正常，不表示有问题）。

3. **触发 update 恢复陷阱**：`hermes gateway status` 可能触发之前中断的 `hermes update` 恢复流程（自动 pip install）。若报 `cryptography ... RECORD 文件缺失 / 拒绝访问 (os error 5)`——文件被运行中的 Hermes 占用，属正常，不影响 gateway 启动（错误后仍会 `Scheduled Task registered` + `Gateway process running`）。

## 二、重启 gateway 并确认恢复

```bash
hermes gateway restart        # 或 hermes gateway start
sleep 5
grep -iE "feishu connected" ~/AppData/Local/hermes/logs/gateway.log | tail -1
```
预期：`✓ feishu connected`（websocket 模式）。同时确认 `Gateway running with N platform(s)`。

**⚠️ 关键认知：飞书 WebSocket 断连期间的消息不会自动补推**——重连后只能收到新消息，停机窗口（停机时间→重启时间）内的消息**必须手动拉取**。不要以为重启就完事了。

## 三、拉取停机窗口消息（核心）

停机窗口 = [停机时间, 重启时间]，示例 `2026-08-07T10:56:00+08:00` → `2026-08-07T14:18:00+08:00`。

1. **收集候选 chat_id**：从 `~/AppData/Local/hermes/sessions/sessions.json` 提取（session_key 格式 `agent:main:feishu:dm:oc_xxx` 或 `group:oc_xxx`）：
   ```python
   import json
   data = json.load(open(r'C:/Users/HMSJ/AppData/Local/hermes/sessions/sessions.json', encoding='utf-8'))
   seen = {}
   for k, v in data.items():
       if k.startswith('_'): continue
       parts = v.get('session_key', k).split(':')
       if len(parts) >= 5 and parts[2] == 'feishu':
           seen[parts[4]] = parts[3]
   for cid, ct in sorted(seen.items()): print(cid, '|', ct)
   ```
   ⚠️ sessions.json 里的 chat_id 有**失效项**（旧应用/已移除，bot 不在其中），需过滤。

2. **逐个会话拉窗口消息**（bot 身份，`--chat-id`）：
   ```bash
   lark-cli im +chat-messages-list --chat-id "<oc_xxx>" --as bot \
     --start "2026-08-07T10:56:00+08:00" --end "2026-08-07T14:18:00+08:00" \
     --order asc --page-all
   ```
   - **坑：返回字段是 `data.messages`，不是 `data.items`**（曾因此误判"无消息"）。解析用 `d['data']['messages']`。
   - `--page-all` 自动翻页；`--order asc` 按时间正序。
   - 每条消息：`create_time`（已格式化）、`sender.name`（真名）、`content`。

3. **过滤无效会话**：bot 不在会话返回 `code 230002 (Bot/User can NOT be out of the chat)`——跳过。PARSE_ERR（非 JSON 输出）时先 `2>&1 | head -c 500` 看原始错误，基本都是 230002。

4. **确认 bot 真正在的会话**（可选）：`lark-cli im +chat-list --as bot --types=group --page-all`——bot 视角**列不出 p2p 私聊**（飞书限制），只有群。私聊靠 sessions.json 的 chat_id 或 `+chat-messages-list --user-id`（⚠️ `--user-id` 仅限 `--as user`，bot 身份必须 `--chat-id`）。

5. **不要用 `+messages-search`**：需要 `search:message` scope（user 授权里通常没有），会报 `missing_scope`。逐个会话拉更可靠。

## 四、批量补回复

对每个有未回复消息的会话，用 bot 身份补发：

```bash
lark-cli im +messages-send --chat-id "<oc_xxx>" --as bot --text "回复内容"
```

**补回复模板**（用户认可的写法）：
- 先道歉说明：`抱歉！刚才系统宕机了（10:56-14:18），你的消息没及时回复，现已恢复。`
- 再针对消息内容回应：创作类任务（分镜/剧本/提示词）→「你发的 XX 我看到了，重新发我一次，我马上处理」；问答类 → 直接回答。
- 注意：gateway 恢复后部分消息可能已被正常处理（重连后的新消息照常回复），补回复作为宕机说明补充，不冲突。

## 五、验证送达

```bash
lark-cli im +chat-messages-list --chat-id "<oc_xxx>" --as bot --order desc --page-limit 2
```
最新消息的 `sender.name == Hermes` 且时间在发送后 = 送达成功。

## 六、收尾记录

- 更新 skill：遇到新坑（字段名、权限、时序）立即 patch 本节。
- 向用户汇报：停机窗口、未回复人数/消息数、补回复结果、遗留问题（如 cryptography 安装待修）。
- 遗留修复（可选）：中断的 `hermes update` 需在关闭所有 Hermes 窗口后于终端跑：
  ```bash
  cd /d "C:\Users\HMSJ\AppData\Local\hermes\hermes-agent"
  "C:\Users\HMSJ\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" -m pip install -e ".[all]"
  ```

## Pitfalls 速查

| 现象 | 根因 | 处理 |
|---|---|---|
| 飞书不回消息 | gateway 进程停了（非 adapter 问题） | 查 gateway.log 末尾 `Gateway stopped` → 重启 |
| 停机窗口消息丢失 | WebSocket 断连不补推 | 手动 `+chat-messages-list --start/--end` 拉取 |
| 解析全 0 条 | 字段名用错（`data.items` 应为 `data.messages`） | 用 `data.messages` |
| `--user-id` 报 invalid_argument | bot 身份不支持 user-id | bot 用 `--chat-id`，`--user-id` 仅 user 身份 |
| 230002 | bot 不在该会话（旧应用/已移除） | 跳过，查 bot 真实会话 |
| `+messages-search` missing_scope | 缺 `search:message` scope | 不用它，逐个会话拉 |
| `hermes gateway status` 触发 pip 恢复且报 cryptography 拒绝访问 | update 中断 + 文件被占用 | 忽略，gateway 照常启动；彻底修复需关 Hermes 后手动 pip |
| 恢复后无人回复「你死了吗」 | 停机窗口消息未补推，用户以为被无视 | 拉消息 → 补回复道歉 |
| watchdog 标记文件每 ~30min 一条「进程不存在」，但 gateway 实际正常 | 计划任务环境下 `Get-CimInstance` 读不到其他进程的 CommandLine（权限/会话隔离），按命令行匹配必然返回空 → 误判宕机拉起 | 检测判据改为：①端口 8644 LISTENING（netstat 主判据，不依赖 CommandLine 权限）②日志 <10min 新鲜（覆盖重启窗口期）③命令行匹配兜底。注意 netstat 中文系统输出 GBK，subprocess 要 `errors="replace"` |
| 修完误报后遗留 15 条假宕机记录 | 标记文件 outages 历史是脏数据 | 清空 `gateway_outage.json` 的 `outages` 列表，`last_outage_reason` 注明已修复 |

## 前置条件

- lark-cli 已配置 bot 身份（`lark-cli auth status` → bot ready）
- gateway 日志在 `~/AppData/Local/hermes/logs/gateway.log`
