# 飞书 SDK 消息查询/编辑实操（lark-cli 未封装时）

2026-08-07 实测：lark-cli `im messages` 无 list/update 子命令（只有 delete/forward/merge_forward/read_users/urgent_*），`+messages-search` 需 user 身份 + `search:message` scope（未授权）。查群消息/编辑已发消息用 lark_oapi SDK 直连。

## 凭据

Hermes bot 应用凭据在 `%LOCALAPPDATA%/hermes/.env`（`FEISHU_APP_ID` / `FEISHU_APP_SECRET`，app=cli_aafaf3e37ef89cc2）。lark-cli 自己的 `~/.lark-cli/config.json` 是另一个 app（user 身份）——别混。

```python
env = {}
for line in open(r'C:/Users/HMSJ/AppData/Local/hermes/.env', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); env[k] = v.strip()
import lark_oapi as lark
client = lark.Client.builder().app_id(env['FEISHU_APP_ID']).app_secret(env['FEISHU_APP_SECRET']).build()
```

## 列群消息（找 message_id）

```python
from lark_oapi.api.im.v1 import ListMessageRequest
req = ListMessageRequest.builder().container_id_type('chat').container_id('oc_xxx') \
    .sort_type('ByCreateTimeDesc').page_size(20).build()
resp = client.im.v1.message.list(req)
for it in resp.data.items:
    print(it.create_time, it.msg_type, it.sender.sender_type, it.message_id)
```

**坑**：
- **必须 `sort_type='ByCreateTimeDesc'`** 才能从最新消息拿（默认正序，最新消息在最后一页，page_size=20 只拿最旧的）
- `start_time` 参数有坑：传毫秒时间戳报 `230001 end_time is earlier than start_time`（疑似 SDK 默认值问题）——用 sort_type 替代
- `it.create_time` 是字符串，用 `int(it.create_time)/1000` 转时间戳
- bot 消息判断：`it.sender.sender_type == 'app'`；撤回的消息仍会出现在列表里

## 编辑已发消息（如清除投递内容里的工具噪音）

```python
from lark_oapi.api.im.v1 import UpdateMessageRequest, UpdateMessageRequestBody
# post payload 重建：复用 Hermes adapter 的 markdown→post 转换
import sys; sys.path.insert(0, r'C:/Users/HMSJ/AppData/Local/hermes/hermes-agent/plugins/platforms/feishu')
from adapter import _build_markdown_post_payload
payload = _build_markdown_post_payload(clean_markdown_text)
body = UpdateMessageRequestBody.builder().msg_type('post').content(payload).build()
req = UpdateMessageRequest.builder().message_id('om_xxx').request_body(body).build()
resp = client.im.v1.message.update(req)
```

**坑**：
- builder 方法是 **`request_body`** 不是 `body`（`UpdateMessageRequestBuilder` 无 body 方法，会 AttributeError）
- 编辑后验证：list 该消息 content，确认目标噪音已消失（注意消息本体存的是 markdown 原文，飞书客户端渲染时中英文间会加空格——核对时用无空格原文，别被渲染差异误判"缺失"）

## 撤回消息

```bash
lark-cli im messages delete --message-id <om_xxx> --as bot --yes
```

高危操作：lark-cli 默认要求确认（confirmation_required），**agent 不能自己加 --yes**，须用户明确确认后才能执行。

## 内容清理模板

投递内容混入 File-mutation verifier 噪音时的处理：从 cron 输出文件（`cron/output/<job_id>/<时间戳>.md`）的 `## Response` 段取原始内容 → 截断到噪音起点（`resp.find('File-mutation verifier')`）→ 去结尾孤立 emoji（如 ⚠️）→ `_build_markdown_post_payload` 重建 → update。
