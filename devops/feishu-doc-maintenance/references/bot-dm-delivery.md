# Bot 私发文档到指定用户 DM —— 完整配方

> **适用场景**：用户说「把这个发给我」「把这个发到 XX 会话」「给 YY 发文档」
> 「把 XX 通过飞书发给 YY」「通过飞书文档发给 YY」。**bot 身份合规**——
> 满足「Hermes bot 身份发对外消息」铁律（2026-08-13 确立）。
>
> 本配方是 `feishu-doc-maintenance` 第四节「bot 身份创建文档 + 权限开通」的
> 延伸——加上 IM 端的 DM 投递闭环，构成「bot 私发文档给指定用户」全流程。

---

## 0. 前置核查（必做）

### 0.1 用户在职 + open_id 解析

发任何消息给一个人前，**必须先核查人员在职状态**——open_id 在评论历史里出现过
不代表该人现任（参考叶子 ou_7c8f735a 2026-09 已离职的踩坑）。

```bash
# 查人（bot 可用）
lark-cli contact +get-user --user-id <ou_xxx> --as bot
```

返回 `name: "用户133976"` 这种脱敏名时，**字段差异实锤**——该用户飞书账号未设姓名，
真名在 `localized_name`（仅 user 身份 `+search-user` 返回）。

拿不到 open_id 时：
- 查 Obsidian 画像：`成员画像/<姓名>.md` 的 frontmatter 有 `open_id`
- 查 state.db 的 sessions 表按 user_id 反查
- 都不行就问用户

### 0.2 目标会话归属（避免发错 DM）

「发到 XX 的会话」要分清：
- **p2p 私聊**（1 对 1 DM，如「和魏宁馨的会话」）→ `--user-id <ou_xxx>` 即可
- **群聊**（如「魔王六人群」）→ `--chat-id <oc_xxx>`，需要事先 `im +chat-list` 拿 chat_id
- **多人群/项目群** → 同上，先 list 再 send

---

## 1. 准备源文件

源文件三种形态：

| 形态 | 处理 |
|------|------|
| Markdown 笔记 | 直接用，传 `--content @file.md`（走 markdown 格式，CLI 自动渲染表格） |
| docx 文件 | 先用 `scripts/docx_to_feishu_markdown.py` 转 md（**保留段落+表格顺序**） |
| 即兴文本 | 写进临时 .md 文件 |

### docx → markdown（保表格顺序）

```bash
python 'C:/Users/HMSJ/AppData/Local/hermes/skills/devops/feishu-doc-maintenance/scripts/docx_to_feishu_markdown.py' \
  --input "C:/.../input.docx" \
  --output "C:/Users/HMSJ/AppData/Local/Temp/_feishu_push.md"
```

**关键点**：脚本必须按 `body.iterchildren()` 顺序遍历，**段落和表格交错**保留——
只遍历 `d.paragraphs` 会丢表格（python-docx 的 `paragraphs` 列表**不含表格**）。

---

## 2. 三步发文档

### 2.1 bot 创建 Doc

```bash
cd <tmp 目录>   # @file 只能读 cwd 相对路径
lark-cli docs +create \
  --doc-format markdown \
  --title "<文档标题>" \
  --content @<source.md> \
  --parent-position my_library \
  --as bot
```

返回：

```json
{
  "ok": true,
  "data": {
    "document": {
      "document_id": "XmEvdz7bZosXHMxBJs2cR2sonNe",
      "url": "https://ucn8khyb55ax.feishu.cn/docx/XmEvdz7bZosXHMxBJs2cR2sonNe"
    },
    "permission_grant": {
      "user_open_id": "ou_68719...（bot 自己）",
      "perm": "full_access"
    }
  }
}
```

**坑**：bot 只会给自己开 full_access。**目标用户默认无权限，必须显式开权限。**
（详见第四节「权限开通」）

### 2.2 给目标用户开 view

```bash
lark-cli drive +member-add \
  --token "<document_id>" \
  --type docx \    # ← 必须加，裸 token CLI 推不出类型
  --member-type openid \
  --member-id "<ou_目标用户>" \
  --perm view \    # 接收方只需 view，不必 edit
  --as bot \
  --yes
```

不加 `--type` 报错：

```
{"ok": false, "error": {"type": "validation", "subtype": "invalid_argument",
 "message": "--type is required when --token is a bare token; ...",
 "param": "--type"}}
```

### 2.3 在目标用户 DM 发链接

```bash
lark-cli im +messages-send \
  --user-id "<ou_目标用户>" \
  --markdown '<一句话简介>

🔗 <url>' \
  --as bot
```

**用 `--user-id` 而不是 `--chat-id`**——CLI 会自动解析 p2p chat_id。

bot 身份 `--as bot` 是合规铁律——不要用 `--as user` 冒充用户本人。

---

## 3. 验证三件套（必做）

每一步发完都验证，不能光看 API 返回 ok。

### 3.1 验证权限开到位

```bash
lark-cli drive +member-list --token "<document_id>" --type docx --as bot
```

返回里应能看到目标 ou_ 出现 + `perm: "view"`。

### 3.2 验证消息发到对的 chat

```bash
lark-cli im +messages-mget --message-ids "<om_xxx>" --as bot
```

返回里：
- `sender.name`: "Hermes"（确认 bot 身份）
- `sender.sender_type`: "app"（app sender = bot）
- `chat_id`: 应匹配目标 DM（p2p 用 oc_ 开头）
- `message_app_link`: 形如 `https://applink.feishu.cn/client/chat/open?openChatId=oc_xxx`

### 3.3 验证用户身份 + 在职

```bash
lark-cli contact +get-user --user-id "<ou_xxx>" --as bot
```

返回 `name` 字段，看是否脱敏（用户133976）——确认账号可用 + 真名对照画像档案。

---

## 4. 实战案例：2026-09-02 中国古剑器物档案 → 魏宁馨 DM

**任务**：把一份桌面 docx（46 KB，含 11 张表格）以飞书云文档形态发给魏宁馨。

**步骤**：

1. docx → md：用 `scripts/docx_to_feishu_markdown.py` 转出 7947 字符 md（18 表格完整）
2. bot 创建 Doc：document_id = `XmEvdz7bZosXHMxBJs2cR2sonNe`
3. 给魏宁馨（`ou_94566a9aab7dbe27afe38d759e80c534`）开 view
4. 在 DM `oc_a856f8f1e2fc25c61185ab0191133c00` 发链接

**验证矩阵**：
- `+member-list` → 魏宁馨 `perm: "view"` ✅
- `+messages-mget` → sender=Hermes bot, chat_id=魏宁馨 DM ✅
- `+get-user` → 真名=用户133976（脱敏）/open_id 匹配画像档案 ✅

**耗时**：5 步共 6 分钟（其中 4 分钟是首跑 `lark-cli contact`/`docs --help` 探路）。

---

## 5. 常见踩坑

### 5.1 bot 默认只给自己 full_access

`docs +create --as bot` 返回里 `permission_grant.user_open_id` 是 **bot 自己**
（`cli_aafaf3e37ef89cc2` 对应的 `ou_68719743...`），不是 owner user。
**目标用户默认无访问权**——必须显式 `drive +member-add --perm view` 开权限，
否则对方点链接会「无权限」。

### 5.2 `--type docx` 别忘

`+member-add` 接 `--token` 裸 document_id 时，CLI 推不出资源类型，**必须**手动
`--type docx`，否则报「--type is required when --token is a bare token」。

### 5.3 「把这个对话发给我」的歧义

用户说「从这个对话发给我」「把这份档案发给我」要分清：
- 「我」= 当前会话的人（妖玉本人）→ 发到当前飞书会话
- 「我」= 提到的另一个人（如「和魏宁馨的会话」）→ 发到对应 DM
- 模糊时**先列选项 + 让用户拍板**，不要猜（猜错发错地方比不发更糟）

### 5.4 中文用户姓名查 open_id

bot 身份 `+get-user` 返回的 `name` 字段可能是脱敏的「用户+N」格式。
**不能因此判定对方不在职或无权限**——这是该用户飞书账号未设姓名的字段问题，
不是权限问题。真名去 Obsidian `成员画像/<姓名>.md` 找 frontmatter `open_id`。

---

## 6. 性能参考

| 步骤 | 耗时 |
|------|------|
| `+get-user` 反查 | <1s |
| docx → md（46 KB） | <1s |
| `docs +create` | 2-3s |
| `drive +member-add` | 1-2s |
| `im +messages-send` | 1-2s |
| **总耗时** | **~10s**（不含人名/路径决策思考） |

熟人的常规推送，10 秒闭环。