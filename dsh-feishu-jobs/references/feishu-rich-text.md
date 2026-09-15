# 飞书富文本投递：准确字段格式

照直觉写会**静默失败**——接口返回 `ok:true`，但内容不对/看不到。以下格式全部经 `--dry-run` 或实发验证。

## 一、评论回复的富元素

命令：`lark-cli drive +add-reply --url <doc> --comment-id <id> --content @file --as bot`

`--content` 是 `reply_elements` 的 JSON 数组。**值放在与 `type` 同名的字符串字段里**：

| 输入（正确） | lark-cli 转换出的最终 API body |
|---|---|
| `{"type":"text","text":"正文"}` | `{"type":"text_run","text_run":{"text":"正文"}}` |
| `{"type":"mention_user","text":"@全志越","mention_user":"ou_..."}` | `{"type":"person","person":{"user_id":"ou_..."}}` |
| `{"type":"link","text":"标签","link":"https://..."}` | `{"type":"docs_link","docs_link":{"url":"..."}}` |

### 两个静默失败

```jsonc
// 错：用 user_id。不报错，但 lark-cli 把 text 的值当 user_id
{"type":"mention_user","text":"@全志越","user_id":"ou_..."}
//   → person.user_id = "@全志越"    静默 @ 不到任何人

// 错：link 用对象。会报 cannot unmarshal object into ... .link of type string
{"type":"link","text":"标签","link":{"url":"https://..."}}
```

### 读取侧字段名不同（不对称）

`drive +list-comments` 返回的是 `{type, text_run:{text}, person:{user_id}, docs_link:{url}}`。
写入用 `mention_user`/`link`，读出来是 `person`/`docs_link`。

### 确定 schema 的唯一可靠手段

```powershell
lark-cli drive +add-reply --url <doc> --comment-id <id> --content "@<file>" --as bot --dry-run
```

`--dry-run` **校验并打印完整请求体但不发送**。写代码前先看它输出的 `body.content.elements`，那是最终 API 形态。`--help` 只列类型名，不够。

### 不可回复的评论

`is_whole=true`（整篇评论）与 `is_solved=true`（已解决）**不接受回复**。发之前先 `+list-comments` 查状态。

### 其他约束

- `--content` 支持 `@file`，长内容必用（内联 JSON 在 PowerShell 下会被吞引号）
- 身份必须 `--as bot`
- 单元素数组要手工拼 `[` + 元素 + `]`：PS 5.1 的 `ConvertTo-Json` 会把单元素数组塌成对象

## 二、交互式卡片（IM 投递）

发消息走原始 API（lark-cli 无 im send 快捷命令）：

```
POST /open-apis/im/v1/messages?receive_id_type=chat_id
body: { receive_id, msg_type: "interactive", content: "<卡片 JSON 的字符串>" }
```

`content` 是**卡片 JSON 的字符串**（双重编码）。

### 必须用旧版 schema

```json
{
  "config": { "wide_screen_mode": true },
  "header": {
    "template": "blue",
    "title": { "tag": "plain_text", "content": "GitHub 项目日报 · 9月15日" }
  },
  "elements": [
    { "tag": "div", "text": { "tag": "lark_md", "content": "**分节标题**\n- 列表项" } },
    { "tag": "hr" },
    { "tag": "note", "elements": [ { "tag": "plain_text", "content": "落款" } ] }
  ]
}
```

**schema 2.0 不可用**：某些租户/客户端会返回 `"请升级至最新版本客户端，以查看内容"` 并降级渲染 —— 接口仍返回 `ok:true` / `message_id`，**日志看起来完全成功**。发卡片后务必检查响应体里有没有「请升级」字样（参考实现会把它标记成 `CARD-DEGRADED`）。

### `lark_md` 的能力边界

支持：粗体 `**x**`、斜体 `*x*`、删除线、链接 `[文字](url)`、`@`、emoji、换行、`-` 列表、`>` 引用。

**不支持：标题（`#`）与表格。**

→ 标题行转成 `**粗体**` 的 `div`；分节之间插 `{tag:'hr'}`；表格改列表或拆成多个 `div`。

### 卡片体积

卡片 JSON 上限约 30KB，比纯文本宽松得多。参考实现把正文截到 6000 字符并注明「完整输出见任务日志」。

## 三、纯文本消息（对照）

```json
{ "receive_id": "oc_...", "msg_type": "text", "content": "{\"text\":\"正文\"}" }
```

飞书文本消息的 `content` 也是 JSON 字符串。单条约 3500 字上限，超长会被截或报错——**长内容用卡片**。

## 四、身份与 chat_id

- open_id 是 **app 维度**的：同一个人在不同 app 下 open_id 不同，不可跨 app 混用
- 查名字：`lark-cli api GET /open-apis/contact/v3/users/<open_id> --params '{"user_id_type":"open_id"}' --as bot`
- 用 DM 投递需要的是**该 bot 与该用户的 p2p chat_id**，与别的 bot 的 DM chat_id 不通用
- bot 身份看不到 p2p 会话列表（隐私保护），只能从既有会话记录里取
