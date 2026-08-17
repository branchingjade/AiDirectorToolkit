# 飞书 cron 投递失败 [99992402] field validation failed 排障（2026-08-07 实测）

## 症状

cron job 的 `last_delivery_error`：
```
live adapter send failed: [99992402] field validation failed; live adapter delivery to feishu:oc_xxx failed: [99992402] field validation failed; delivery error: Feishu send failed: [99992402] field validation failed
```
live adapter 和 standalone fallback 都失败。job 本身 `last_status=ok`（agent 执行成功，只是投递挂）。

## 根因

**job 创建于飞书话题线程** → origin 快照带 `thread_id`（omt_xxx）→ cron live adapter 投递时 route_metadata 带 thread_id → DeliveryRouter 把 thread_id 塞进 send_metadata → 飞书 adapter（`plugins/platforms/feishu/adapter.py` `_feishu_send_with_retry`）见 metadata.thread_id 就改用 `receive_id=thread_id, receive_id_type=thread_id` 创建消息 → 飞书 API 对 **post 类型 + thread_id 路由组合**返回 99992402 field validation failed。

相关代码点：
- `cron/scheduler.py` ~1739-1830：live adapter 投递，route_metadata 带 thread_id
- `gateway/delivery.py` 604-605：`send_metadata["thread_id"] = target_thread_id`
- `plugins/platforms/feishu/adapter.py` 4820-4828：thread_id 作 receive_id 创建消息
- adapter 4737 行注释确认 audio 消息 thread 路由同样 99992402（post 无 fallback，属上游缺口）

## 判定（3 步内定位）

1. 读 jobs.json 对比所有 job 的 deliver/origin：
   ```python
   python3 -c "import json; d=json.load(open(r'C:/Users/HMSJ/AppData/Local/hermes/cron/jobs.json',encoding='utf-8')); [print(j.get('name','?')[:14], '|', j.get('deliver'), '| thread:', (j.get('origin') or {}).get('thread_id')) for j in d]"
   ```
   **唯一致病特征 = deliver=origin 且 origin.thread_id 非 None**。其余 job 显式 deliver（`feishu:oc_xxx`）+ thread_id=None 全部正常。
2. 手动 `lark-cli im +threads-messages-list --thread-id omt_xxx --as bot` 验证 thread 存在（存在≠可用，post 组合仍被拒）。
3. 手动 `+messages-send --text` 成功 + `--msg-type post --content <payload>` 成功 → 通道和内容都没问题，锁定为 thread 路由。

## 修复

```bash
# deliver 从 origin 改为显式群地址（去 thread 路由）
cronjob update --job-id <id> --deliver feishu:oc_685820a739882df67954e0923ec9ab73
# 实测验证
cronjob run --job-id <id>   # last_delivery_error 变 null 即成功
```

## 排障工具链（lark-cli 细节）

- `im +chat-get` **不存在**（unknown subcommand）→ 验证群用 `im +chat-members-list --chat-id oc_xxx --as bot`
- `im +threads-messages-list --thread-id omt_xxx` 列出话题内消息（验证 thread 有效性）
- `im messages delete` 是 high-risk-write，**需要用户确认，agent 不得自行加 --yes**（lark-cli help 明示）
- `+messages-send --dry-run` 只验证请求形状（不查 bot 成员关系、不查 API 接受度）——真发才作数
- post payload 本地生成：`sys.path.insert(0, r'C:/Users/HMSJ/AppData/Local/hermes/hermes-agent/plugins/platforms/feishu'); from adapter import _build_markdown_post_payload`（返回 `{"zh_cn": {"content": [[{"tag":"md","text":...}]]}}` JSON 字符串）
- **MSYS /tmp 陷阱**：git-bash 的 `/tmp` 与 Windows Python 的 `/tmp` 不是同一路径——python3 写 `/tmp/x.json` 后 bash `cat /tmp/x.json` 找不到。跨工具写文件必须用显式绝对路径（如 `C:/Users/HMSJ/AppData/Local/hermes/cron/output/xxx.json`）

## 旁证：agent self-report 需验证

cron job 的简报声称「本轮新增 N 条评论」**不代表评论真挂上了**（实测 file-mutation verifier 显示 agent 写 6 个 JSON payload 全被语法校验拒绝，但最终评论仍通过其他路径挂载成功）。验证评论实际落库：`lark-cli drive file.comments list --params '{"file_token":"<TOKEN>","file_type":"docx","page_size":100}'`，按 create_time 时间戳确认新增条数。
