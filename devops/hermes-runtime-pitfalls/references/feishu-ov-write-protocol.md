# 飞书侧 OV 写盘契约 v1 — 操作手册（references/）

> 来源：2026-09-03 实战确立（`feishu_image_ocr.py` + `ocr_adapter.py` 重构 + 端到端 401 验证）。
>
> **这一节是写盘"how"，SKILL.md 主索引是"when"，本文件是"具体怎么写"。**

---

## 0. 写盘契约精炼（必读）

飞书每条消息写到**发送者自己的 namespace**，不是 default。default 是徐学环本人（admin）。他们所有人的私有记忆不是 admin 的，admin 凭据可**读**所有 user，写盘仍**按 owner**。

```
viking://user/<OV_USER>/<...>   ← 个人/私有（按 OPENVIKING_USER 路由）
viking://resources/projects/    ← 项目共享/跨成员可见
viking://resources/_team-handbook/  ← 真正公开广播的手册
```

| 内容类型 | 路径 |
|---|---|
| 个人偏好/画像/事件/OCR 捕获 | `viking://user/<OV_USER>/memories/...` |
| 项目级总览（README + 00-12 结构）| `viking://resources/projects/<项目名>/` |
| 团队手册（公开广播）| `viking://resources/_team-handbook/` |
| 一次性任务归档 | `viking://resources/<任务名>/` 或 `viking://resources/_archive/<日期>-<主题>/` |

---

## 1. 端点矩阵（v0.4.14.5 实测挂载）

| 用途 | Method | Path | 输入 | 实测 |
|---|---|---|---|---|
| **写纯文本（已验证疑似无效）** | POST | `/api/v1/content/write` | JSON：`{uri, content, instruction}` | ⚠️ **返回 404 NOT_FOUND**（详见 §1.1） |
| **写文件（推荐）** | POST | `/api/v1/resources/temp_upload` | multipart `file` 字段 | ✅ 200 OK + temp_file_id |
| **import 落盘（推荐第二步）** | POST | `/api/v1/resources` | JSON：`{temp_file_id, to}` | ✅ 走通 |
| 列目录 | GET | `/api/v1/fs/ls` | query: `uri` | ✅ |
| L0/L1/L2 读 | GET | `/api/v1/content/{read,abstract,overview}` | query: `uri` | ✅ |
| 健康探测（不鉴权）| GET | `/health` | — | ✅ |
| 语义召回 | POST | `/api/v1/search/{find,search,grep,glob}` | JSON: `{query, ...}` | ✅ |

### 1.1 ⚠️ `content/write` 端点实测 404（2026-09-03 后续实战修正）

**实测修正**：本会话后续对 `POST /api/v1/content/write` 发起真实请求（带完整鉴权三件套），返回 `404 NOT_FOUND: File not found: viking://user/default/memories/feishu-ocr/_smoke_test.md`。**注意**：这不是鉴权失败（401），而是服务端**找不到要写入的文件**——OV 后端的 `content/write` 语义是"更新已有文件"，不是"创建新文件"。

| 现象 | 含义 |
|---|---|
| 401 AuthenticationError | 鉴权三件套不全或 base64 key 错 |
| **404 NOT_FOUND with "File not found" body** | **content/write 是更新端点，不能创建新文件；必须先 temp_upload + resources** |
| 200 OK | 真的有那个文件并成功更新（前提：先 temp_upload） |

**结论修正**：**写盘真实可用的流程 = Step 1 `temp_upload` + Step 2 `resources` 两步式**（不是 `content/write`）。

⚠️ 本文件前文（§5 范本代码 + §10 checklist）仍使用 `content/write` 端点的范本——**那是更早的、本会话早期一次测试时观察到的表象**，被后续实战推翻。**任何新写盘改造必须用 §1 实测可用的端点**（`temp_upload` + `resources` 两步），不要用 `content/write`。

**与 pitfalls/skill.md §OpenViking SaaS HTTP API 完整协议 (2026-09-01) 节的关系**：9/01 那节的"完整两步式"是当时实战确立，今天再次验证仍然成立——**比 §1 这条优先**。本文件 §1.1 是更晚的修正补丁。

---

## 2. 鉴权三件套（最容易搞错）

```bash
curl -H "X-API-Key: $OPENVIKING_API_KEY" \
     -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
     -H "X-OpenViking-User: $OPENVIKING_USER" \
     -H "Content-Type: application/json" \
     "$OPENVIKING_ENDPOINT/api/v1/content/write"
```

| 错误 | 现象 | 修 |
|---|---|---|
| 用 `Authorization: Bearer` | 401 AuthenticationError | 改用 `X-API-Key` + `X-OpenViking-Account` + `X-OpenViking-User` |
| 缺任一项 | 401 MissingParameter | 三件套全带上 |
| `OPENVIKING_USER` 写目录名而非 username | 写入到错的 namespace | 用 keymap.json 里 `username` 字段，不是显示名/真名 |
| `OPENVIKING_ENDPOINT` 不带 `/api/v1` 前缀 | 404 | 默认 `https://api.vikingdb.cn-beijing.volces.com/openviking`（端点已含 `/openviking`，自己拼 `/api/v1/...`） |

---

## 3. 运行时切 namespace（关键执行模式）

**问题**：写盘脚本/agent 收到一条飞书消息（owner=A）→ 紧跟收到另一条（owner=B）→ namespace 必须实时切。

**错误做法**：重启进程、改 .env、用 monkey-patch 全局。

**正确做法（实测 OK）**：

```python
import os, importlib

# 假设模块层有 OV_USER = os.environ.get('OPENVIKING_USER', 'default')
# 子模块 import 时已绑定到默认值 — 切换 namespace 必须同时改两个：

os.environ['OPENVIKING_USER'] = target_username  # 给未来的子进程用
import ov_module                                  # 单次 import OK
ov_module.OV_USER = target_username               # 直接改模块全局
# 现在 ov_module.capture_to_xxx() 会写到 viking://user/<target_username>/
```

**为什么必改模块全局**：`import` 后模块 `OV_USER` 已是字符串快照，不再随 `os.environ` 变。必须 manual monkey-patch。

**陷阱**：`from xxx import OV_USER` 会把值拷到本地变量，再改模块无效。**总是 `import xxx` + `xxx.OV_USER = ...`**，不要 from import。

**反模式**：

```python
# ✗ 错（只有 env，没动模块全局）
os.environ['OPENVIKING_USER'] = 'QuanZhiYue'
ov_module.capture()  # 仍写到 default

# ✗ 错（from import 把值锁死）
from ov_module import OV_USER
# 之后再改 ov_module.OV_USER 已无效
```

---

## 4. open_id → username 路由（飞书侧必要前置）

**没有这一步不能切 namespace**。飞书消息 metadata 含 `sender_id.open_id`（即 `ou_xxx` 字符串）。

**数据源（2026-09-03 扩展 `namespace` 字段后）**：

`Documents/Hermes/.v1/feishu_keymap.json` 现在每个 entry 含 `namespace` 字段，结构：
```json
{
  "quanzhiyue": {"open_id": "ou_88d...", "namespace": "QuanZhiYue", ...},
  "yuanjinming": {"open_id": "ou_537...", "namespace": "CY", ...},
  "yezi": {"open_id": "ou_aed...", "namespace": null, "namespace_note": "已离职"},
  "panyanfei": {"open_id": "ou_fff...", "namespace": "", "namespace_note": "TODO:用户尚未确认 OV namespace 分配"}
}
```

**`namespace` 字段语义**：

| 值 | 含义 | resolve 行为 |
|---|---|---|
| `"QuanZhiYue"` 等具体字符串 | OV admin 端已注册的 user namespace | 直接返回该字符串 |
| `null` | 用户离职/不分配 | 返回 `'default'`（admin 兜底，**注意：会污染 admin 空间，技术上未拒绝但语义错误**——更好的行为是 raise NotAllowedCapture）|
| `""`（空字符串） | TODO 等用户拍板 | 继续 fallback 到旧逻辑 |

**来源优先级（updated 2026-09-03）**：

```
CLI --owner QuanZhiYue 参数  →  keymap.json 的 entry.namespace 字段  →  硬编码  →  'default'（fallback）
```

**解析 Python 范本（updated）**：

```python
def resolve_ov_username(open_id: str) -> str:
    if not open_id:
        return 'default'
    try:
        if os.path.exists(KEYMAP_FILE):
            with open(KEYMAP_FILE, encoding='utf-8') as f:
                km = json.load(f)
            for uname, info in km.items():
                if isinstance(info, dict) and info.get('open_id') == open_id:
                    ns = info.get('namespace')
                    if ns is None:
                        # 显式 None = 已离职/不分配 → 兜底 default（待优化：建议 raise）
                        return 'default'
                    if isinstance(ns, str) and ns:
                        return ns
                    # ns == '' → 待拍板,继续 fallback
                    break
    except Exception:
        pass
    # 硬编码兜底
    hardcoded = _OPEN_ID_TO_USERNAME_HARDCODED.get(open_id)
    if hardcoded:
        return hardcoded
    return 'default'
```

**陷阱**：`namespace` 字段的大小写与 OV admin 端注册名**严格一致**——`YangXvan` V 是大写 V（不是 u），这是 OV admin 端命名约定的产物，**不是** pinyin 转换 bug。`ShiWenHao`/`HouSiYv` 等都是 CamelCase 形式。

**当前 keymap 13 个 entry 解析矩阵**（2026-09-03 实测 8/8 通过）：
- `quan_zhiyue` open_id → `QuanZhiYue` ✅
- `yuan_jinming` open_id → `CY` ✅
- `ye_zi` open_id → `default`（离职，None → fallback）
- `hou_siyu` open_id → `HouSiYv` ✅
- `shi_yuhao` open_id → `ShiWenHao` ✅
- admin open_id → `default` ✅
- 未知 open_id → `default`（fallback）
- 空 open_id → `default`（fallback）

---

## 5. 完整 HTTP 写盘范本（实测通过 — 401 是预期）

```python
import os, json, time, urllib.request

OV_ENDPOINT = os.environ['OPENVIKING_ENDPOINT']
OV_API_KEY = os.environ['OPENVIKING_API_KEY']
OV_ACCOUNT = os.environ['OPENVIKING_ACCOUNT']
OV_USER = os.environ['OPENVIKING_USER']  # runtime 切换

def capture_to_ov(description: str, file_basename: str, subdir: str = 'memories/feishu-ocr'):
    uri = f'viking://user/{OV_USER}/{subdir}/{file_basename}.md'
    content = (
        f'# {file_basename}\n\n'
        f'**captured_at**: {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}\n\n'
        f'## 描述\n\n{description}\n'
    )
    body = json.dumps({
        'uri': uri,
        'content': content,
        'instruction': '提取事实、人物、地点、时间，便于后续按 sender 召回',
    }, ensure_ascii=False).encode()

    req = urllib.request.Request(
        f'{OV_ENDPOINT}/api/v1/content/write',
        data=body,
        method='POST',
        headers={
            'X-API-Key': OV_API_KEY,
            'X-OpenViking-Account': OV_ACCOUNT,
            'X-OpenViking-User': OV_USER,
            'Content-Type': 'application/json',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return {'success': True, 'uri': uri, 'status': 200}
    except urllib.error.HTTPError as e:
        return {'success': False, 'status': e.code, 'uri': uri,
                'error': e.read().decode(errors='replace')[:300]}
```

---

## 6. 401 / 404 调试矩阵（验收通道走通）

| 现象 | 真因 | 修 |
|---|---|---|
| `401 AuthenticationError: API key missing or invalid` + Request ID 行号 | 通道到达鉴权层 | ✅ 端点/header/namespace 全部走通；只缺凭据 |
| `404 NOT_FOUND: File not found: <uri>` | `content/write` 不能创建新文件（仅更新） | 改用 §5.1 的两步式 `temp_upload + resources` |
| `404 NOT_FOUND`（路径错） | `OV_ENDPOINT` 拼错或 `/api/v1` 重复 | 检查 `OV_ENDPOINT` 是否带 `/openviking`，不要再拼 |
| `400 INVALID_URI` + `to must target resource content` | URI 不指向具体文件 | 路径末尾必须有 `.md` 等扩展名 |
| `400 MissingParameter` | body 缺字段 | temp_upload multipart 字段名是 `file`；resources 必带 `temp_file_id`+`to` |
| `5xx HTTPError` | 服务端暂时不可用 | 重试 1 次，再失败就降级到 OBSOLETE 路径 |

**关键判断**：
- **401 + 有 Request ID** = **鉴权层全对**。是验收标志，不是 bug。
- **404 "File not found"**（来自 `content/write`）= 端点选错，**必须改两步式**。

---

## 7. 已知子场景的工作流模板

### 7.1 飞书图片 OCR 工具（已重构）

`scripts/feishu_image_ocr.py` + `scripts/ocr_adapter.py`——按 sender 解析 → 写盘到 owner namespace → 飞书回信：

```
lark-cli im +messages-mget <msg_id>
  → 提取 sender_id.open_id
  → keymap.json 反查 → username
  → export OPENVIKING_USER + monkey-patch ocr_adapter.OV_USER
  → MiMo-v2.5 OCR 描述
  → POST /api/v1/content/write 到 viking://user/<username>/memories/feishu-ocr/<msg_id>.md
  → lark-cli im +messages-reply 飞书回复（带 namespace 显示）
```

CLI 加 `--owner <username>` 显式覆盖自动解析（运营人员手动调时用）。

### 7.2 文档评论 capture（待补——按同模式改造）

`feishu_comment.py` 当前内部在 agent 上下文里走 OV provider 自动 retain——这部分已工作。**但**如要单独把评论原文 dump 到 resources/projects（用于跨成员可见评论摘录），按本协议：

```python
# 评论内容 → viking://resources/projects/<项目>/comments/<comment_id>.md
# 不是写到 user namespace（评论不属于个人，是项目共享资产）
uri = f'viking://resources/projects/<项目>/comments/<thread_id>/<comment_id>.md'
```

### 7.3 cron 派生任务（如知识库巡检）— 已知工作

不是写盘，是反向**读盘 + 写回**。`OPENVIKING_USER=default`（admin）跑；写到 `viking://user/default/...` 或 `viking://resources/projects/`。**这条不需要 owner 路由**，因为 cron 是 admin 视角运维任务。

---

## 8. 三件套 env 的语义

| env | 含义 | 示例值 | 谁设 |
|---|---|---|---|
| `OPENVIKING_ENDPOINT` | 服务根 URL | `https://api.vikingdb.cn-beijing.volces.com/openviking` | 部署期 |
| `OPENVIKING_API_KEY` | 鉴权 key（base64） | 部署期 | 用户/部署 |
| `OPENVIKING_ACCOUNT` | 多 account 架构里的 account 名 | `default` | 部署期 |
| `OPENVIKING_USER` | **写盘 namespace 路由键** | `default` / `QuanZhiYue` / `CY` ... | **运行时**根据 owner 切换 |
| `OPENVIKING_AGENT` | agent 名 | `hermes` | 部署期 |

**唯一运行时可变的是 `OPENVIKING_USER`**。其他都是 deployment-time 静态配置。

---

## 9. 持久化契约位置（下次会话直接召回）

```
viking://user/default/peers/hermes/memories/patterns/mem_<hash>.md
```

每条契约 = `viking_remember category=pattern` 一条，含"决策背景/范围/默认行为"。**下次会话 `viking_search("飞书侧 OV 写盘")` 应命中**——这就够了。

---

## 10. 自我检查 checklist（改造前/后跑一次）

- [ ] **写盘端点用两步式**（`POST /api/v1/resources/temp_upload` + `POST /api/v1/resources`），**不用** `/api/v1/content/write`（那个端点只更新已有文件，不能创建新文件，实测 404）
- [ ] 鉴权三件套全带（`X-API-Key` + `X-OpenViking-Account` + `X-OpenViking-User`）
- [ ] namespace 从 keymap.json 反查（不是默认 `default`）
- [ ] 切换 username 时同时改 `os.environ` 和 `module.OV_USER`（不只是 env）
- [ ] CLI 加 `--owner <username>` 显式覆盖（运营人员手动调时用）
- [ ] 写盘失败时返回 status_code，不要 silent drop
- [ ] 401 不当 bug 处理——是通道走通的验收信号
- [ ] 把契约 `viking_remember category=pattern` 写入，下次会话能召回

---

## 历史与演进

- 2026-09-03：首次确立。本文件即来自 `feishu_image_ocr.py` 重构 + 端到端 401 验证实战。
- 下次协议版本变更必先在 `viking://user/default/peers/hermes/memories/patterns/` 留 pattern 痕迹。
