---
name: feishu-comment-test-harness
description: "Use when testing feishu comment pipeline side effects."
version: 1.0.0
tags: [feishu, comment, test, harness, cleanup, side-effect]
related_skills: [feishu-comment-collab]
---

# 飞书评论管线测试 Harness

`feishu_comment.py::handle_drive_comment_event(client, data, *, self_open_id)` **不是 dry-run**——它会跑完整链路：加 reaction、写会话历史、`add_whole_comment` 真发到飞书文档。本 skill 覆盖测试时如何控制副作用、如何清理污染、如何避免「拿 open_id 猜中文姓名把人当成在职」。

## 何时加载

- 验证 `feishu_comment.py` 任何改动（意图检测、prompt 拼接、agent 路由、ACL）
- 给新协作者加 `pairing` 时确认对方在职且中文姓名正确
- 发现飞书文档里有 bot 发的「工具这次连不上」「读全文失败」等看起来像 spam 的 whole comment，要识别是不是测试痕迹

## 不加载场景

- 评论管线的架构/ACL/会话模型 → `feishu-comment-collab`
- 创作润色工作流 → `feishu-comment-creative`

---

## 核心铁律：模拟事件 = 真发评论

**`handle_drive_comment_event` 没有"测试模式"开关**。手工构造 `SimpleNamespace` 事件对象当 `from_open_id=<某人>`，gateway 视角就是真人评论发起者，bot 真发评论到生产文档。

**触发场景**：开发者单元测试、CI 集成测试、agent 自己跑端到端验证——任何"我想看看完整链路跑起来是什么样"的需求。

## 三步测试流程

### 1. 核对人员在职状态（动 pairing 之前）

**不能信**：
- 飞书文档评论历史里出现的 open_id（离职后用户保留权限，feishu 不会下）
- MEMORY.md 里出现的名字（可能是旧记录，新员工可能同名）
- 凭印象把"叶子/杨璇/全志越"硬塞给某个 open_id

**必须做的**：
```bash
# 反查 open_id 的中文姓名
lark-cli contact +get-user --user-id <open_id> --as bot
# 返回 {"name": "<中文姓名>", "open_id": ...}

# 检查是否离职/退出
grep -i <姓名> ~/.hermes/memories/MEMORY.md
session_search query="<姓名> 离职 OR 退出" sort=newest limit=3
```

**判断标准**：
- session_search 最近互动 < 3 个月 = 大概率在职
- session_search 最近互动 > 3 个月 = 高概率离职
- 找不到任何记录 + open_id 在文档评论历史里 = 不知道，问用户
- `contact +get-user` 返 `41012 invalid user` = 不是真人，是 bot 的 mock app user

### 2. pairing add/remove 配对回退

```bash
cd ~/AppData/Local/hermes/hermes-agent
./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules pairing add <open_id>
# ...跑测试...
./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules pairing remove <open_id>
```

**只 add 不 remove = 离职/测试人员被永久加进 approved，未来真评论会触发 bot**。

**测试期间也别动 approved**——除非你**确认**该 user 是真人且在职。即使测试完了，也要回退到原来的 approved 名单（`pairing list` 看）。

### 3. 清理测试产出的飞书评论

**Bot 删不掉自己刚发的 docx whole-comment reply（2026-09-01 实测确认）**：
- `lark-cli drive +delete-reply --as bot` 返 `1069301 fail`
- `lark-cli drive +update-reply --as bot` 返 `1069303 forbidden`
- 飞书 API 权限设计：reply 创建后权限归真人/管理员，不归 bot

**谁删得掉**：
- 用户本人（user OAuth / 飞书 web/客户端右键删）

**替代清理**：用 `lark-cli drive +add-reply --as user` 在污染评论下加 `[测试痕迹 请忽略 - 自动化验证]` 标记 reply，至少让用户看到知道是 bot 测试痕迹。

**预防 > 清理**：
- 用**不存在或测试专用**的 `comment_id`（如新建一个 sandbox 文档专门跑测试）
- 用 `handle_drive_comment_event` 之外的 mock 函数（如果代码允许 mock 注入返回）

## 模拟事件对象构造（Python 模板）

```python
from types import SimpleNamespace
from lark_oapi import Client
from pathlib import Path

env = dict(line.split('=', 1) for line in Path.home().joinpath('.hermes', '.env').read_text(encoding='utf-8').splitlines() if '=' in line and not line.startswith('#'))
client = Client.builder().app_id(env['FEISHU_APP_ID']).app_secret(env['FEISHU_APP_SECRET'].strip('"')).build()

import importlib.util
spec = importlib.util.spec_from_file_location('fc', r'C:/Users/HMSJ/AppData/Local/hermes/hermes-agent/plugins/platforms/feishu/feishu_comment.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

notice_meta = SimpleNamespace(
    file_token="<file_token>",
    file_type="docx",
    notice_type="add_comment",
    from_user_id=SimpleNamespace(open_id="<from_open_id>"),  # 已确认在职的人员
    to_user_id=SimpleNamespace(open_id="<bot_open_id>"),     # 防止被 self-reply filter 跳
)
event_obj = SimpleNamespace(
    event_id="evt_test_<label>",
    comment_id="<real_comment_id>",  # 用 sandbox 文档的 comment_id
    reply_id="",
    is_mentioned=True,
    timestamp="1700000000",
    notice_meta=notice_meta,
)
data = SimpleNamespace(event=event_obj)

asyncio.run(mod.handle_drive_comment_event(client, data, self_open_id="<bot_open_id>"))
```

**坑**：每个 `add_whole_comment` 调用都会**真发到飞书文档**。如果 comment_id 是 sandbox 文档里的，污染有限；如果用真实生产文档的 comment_id，bot 会反复发 whole comment 触发 fake「回复历史」。

## 协作人员 open_id 反查工具

```bash
lark-cli contact +get-user --user-id <open_id> --as bot
# 返回 {"name": "<中文姓名>", "description": "", "open_id": ...}
```

**已知文档协作者（2026-09-01 实战确认）**：
- `ou_68719743e59a5576420e32bb2ea024e1` = **徐学环**（用户本人）
- `ou_7c8f735ad66c252550f265bd392c5d3d` = **杨璇**（已 approved）
- `ou_88d69fdfcf2b532107529f394f3d02a7` = **全志越**（已 approved）
- `ou_32fb7de7b0f9dbb426b413c8c5468ab3` = **无效 user**（返 41012）

任何时候都不应凭"印象 + open_id 后缀"猜姓名——**每次核对都先跑 `+get-user` 反查**。

## 与 feishu-comment-collab 的边界

- **feishu-comment-collab**：架构/ACL/会话模型/Pitfalls（既有）
- **本 skill**：测试 harness + 副作用控制 + 人员核对（新增）

合并到 `feishu-comment-collab` Pitfalls 段是 curator 的活——独立成 skill 是为了清晰边界，等 curator 评估是否合并。

## 相关

- [评论管线架构与 ACL](../feishu-comment-collab/SKILL.md) — 必读前置
- [OpenViking 写入陷阱](../../hermes-runtime-pitfalls/SKILL.md) — 同类型的"客户端不是 dry-run"教训（参考对照思路）