---
name: ov-content-cleanup-workflow
description: OV 内容整改工作流——子代理通览+逐类合并+recall 验证。Use when 清理 OV 旧版/重复/过期卡。
---

# OpenViking 内容整改工作流（2026-09-03 实战确立）

## 何时使用

- 用户要求"清理 OV 内某个项目/类目的旧版/重复卡"
- 用户要求"整理 X 项目总览/进度到 OV"
- 用户拍板"以新正本为准，旧版少许参考价值"
- 用户要求"OV 召回老污染旧版内容"
- 项目重做/角色替换/版本切换后需要 OV 内容批量整改

## 不适用

- 单张卡修正（viking_remember / viking_forget 单卡直接做）
- 跨团队成员的 namespace 写真写盘——admin 不能代写（见下文 §四）
- OV 初始化（用 `references/ov-saas-smoke-test.md`）
- 一次性任务归档（用 `viking://resources/_archive/<日期>-<主题>/`）

---

## 一、第一步：必须先确认"X 是哪个版本"——不要看 OV 旧事件卡推断

任何"整理项目总览/文档现状到 OV"类任务，**第一步必须**：

1. 向用户**直接拍板**当前正本的 token/URL（不要看 OV 旧事件卡推断）
2. 拍板后才能开始"权威源 → OV 总览入口"的对齐工作
3. 旧版来源只能用于"对比说明"，**不能**作为新版文档的引用源

**踩坑教训**（2026-09-03）：第一轮 agent 自己去看 OV 事件卡，找到 `viking://user/default/memories/events/2026/08/28/伏妖记当前文档状态确认.md` —— 信息是「EsMD/NSZK 双正本」——**这是旧版 v2.1.4，已淘汰**。据此写 OV 总览 → 完全错了：把所有"金翅鸟素鸢/暮云亭/依依/沈秋澜"当成新设计，但用户其实已经在 9/2 完成了剧本大重做。用户直接 @ 两个飞书文档 URL 拍板"以这两个为准"——才意识到必须先问用户。

**类级教训**：当用户拍板"以 X 为准"时，agent 不能主动从 OV/记忆库里推断"X 是哪个版本"——必须让用户显式给。MEMORY 里看到的"X"和用户当下指的"X"不一定是同一个东西（版本已迭代多次）。

---

## 二、5 步标准化工作流

### 流程总图

```
[1] 用户拍板"以 X 为准" → 确认 X 是哪个 token/URL/版本
   ↓
[2] delegate_task 子代理通览 OV
   ↓ 报告输出到 C:\Users\HMSJ\Documents\Hermes\分析\<主题>_通览报告_YYYY-MM-DD.md
   ↓ 包含：重复内容、过期内容、可整合偏好、低价值卡、版本演进链
   ↓
[3] 人工审通览报告 + 拍板合并策略（A1/B1/A3 等）
   ↓
[4] 逐类执行（按"先易后难"顺序）：
   ├─ forget 旧版事件卡（按 URI 列表批量）
   ├─ forget 旧版偏好卡
   ├─ forget 旧版实体卡（先读内容确认是过期快照，不是迁移价值）
   ├─ 合并重复偏好（viking_remember 主卡 → forget 旧卡）
   ├─ 建 v2.1.x 历史时间线快照（viking_remember 单卡 + forget 多张）
   └─ 建各成员 profile（viking_remember N 张，按成员 namespace 或 admin 默认）
   ↓ 每次 forget 后 sleep 3-5 秒（OV 后台索引需要时间）
   ↓
[5] 验证 recall
   ├─ 搜新版关键词（应命中新版文档+新事件卡）
   ├─ 搜旧版关键词（应只剩：旧版快照卡 + 历史时间线 + 新版声明"已淘汰"）
   └─ 搜主题+OpenViking 等铁律关键词（应命中铁律卡 rank 1-2）
```

### 第 2 步详细：子代理通览

**派发**：
```python
delegate_task(action='spawn', tasks=[
  {
    goal: "全面盘点 OpenViking viking://user/default/memories/ 下所有可合并/可优化项 ...",
    context: "<背景：2026-09-03 OpenViking 已基本建成团队工作基础设施。前置拍板已落地的有：...>",
    output_schema: {...}
  }
])
```

**显式要求子代理产出**：
- 报告输出到 `C:\Users\HMSJ\Documents\Hermes\分析\<主题>_通览报告_YYYY-MM-DD.md`
- 每条建议含：URI / 触发条件 / 建议操作（合并/降权/forget/保留+理由）
- 控制在 1500-2500 字
- 不要执行任何修改，只产出盘点报告

**子代理自报不可信**——验证方法：报告中的 URI 在 OV 中 recall 能命中。

### 第 4 步详细：执行顺序的关键原则

#### 原则 1：每类合并必须先写主卡再 forget 旧卡（顺序错会丢内容）

```
✅ 正确顺序：viking_remember 新主卡 → 验证主卡到位 → 再 forget 旧卡
❌ 错误顺序：先 forget → 再写（中间窗口旧卡已删，新卡未写 = 数据丢失）
```

#### 原则 2："先看内容再决定"铁律（避免误删）

- ❌ 不要凭通览报告的卡片名直接 forget → 可能误删陈旧但仍有价值的卡
- ✅ 先 `viking_read level=overview` 读每张待删卡片的实际内容 → 确认是过期快照/重复内容 → 再 forget
- ✅ 实体卡迁移类要先确认内容是否真有画像价值（如果只是 2026-08-14 的临时事实，forget 比迁移更干净）

**实战纠正案例**（2026-09-03）：实体卡错位（`entities/人物/` + `entities/团队成员/`）报告是 5 张，实际看内容后发现是 **6 张**（漏了 `entities/飞书成员/徐学环.md`）——子代理报告没全。**先看内容再决定**原则下，不忘不漏。

#### 原则 3：每批操作 ≤10 张 + sleep 3-5s

- OV 后台索引异步，连续 forget 可能撞 503 限流
- `viking_forget` 单卡成功返回 `{"status": "deleted", "estimated_deleted_count": 1}`
- `count = 0` 不是失败（可能是别处已删过）——可继续下一张

#### 原则 4：viking_remember / viking_add_resource 用 `wait=false`

- `wait=true` 模式同步等 L0/L1 语义索引完成，大文件耗时长 + MCP 通道 read timeout 撞上
- 默认 `wait=false`：返回 `{"status": "added", "root_uri": "...", "message": "Resource queued for processing"}` 即视为成功
- 摘要异步生成——10-30 秒后 `viking_browse` 才会看到完整 abstract

---

## 三、recall 验证矩阵（5 项必跑）

| 验证项 | 命令 | 通过标准 |
|---|---|---|
| 目录树可见 | `viking_browse path=viking://resources/projects/<项目>/` | 列出所有上传的文档（abstract 可能 is not ready） |
| 关键词召回命中新版 | `viking_search("项目名 + 新版核心关键词")` | 命中 `viking://resources/projects/...` 的文档，score ≥ 0.45 |
| 关键词召回压制旧版 | `viking_search("项目名 + 旧版核心关键词")` | 新版事件卡/总览 rank 1-2，score ≥ 旧版事件卡 |
| 过期说明召回（agent 自行判断）| `viking_search("项目名 + 已过期/淘汰")` | 命中过期说明事件卡 |
| git 提交（如有 Obsidian 同步）| `git -C <repo> log --oneline` | 看到归档 commit |

**关键词命中策略（决定 recall 排序）**：

- **新版关键词**：当前正本的角色名 + 术语
- **旧版关键词**：被淘汰的角色名 + 术语
- **两个版本在不同 query 路径下不打架**，让 agent 自己判断权威（靠 README 顶部台账）
- **不要试图单一关键词召回同时命中新旧**——会触发 recall 排序混乱

---

## 四、OV 写盘权限边界实测（admin 不能代写其他 namespace）

**实测结果（admin account + 任何 user header 都失败）**（2026-09-03）：

| 尝试 | 结果 |
|---|---|
| `X-OpenViking-Account: default` + `X-OpenViking-User: default` → 写 `viking://user/QuanZhiYue/...` | ❌ PERMISSION_DENIED |
| `X-OpenViking-Account: default` + `X-OpenViking-User: QuanZhiYue` → 写 `viking://user/QuanZhiYue/...` | ❌ PERMISSION_DENIED |
| `X-OpenViking-Account: default` + `X-OpenViking-User: default` → 写 `viking://resources/projects/...` | ✅ 200 OK |

**根因**：OV SaaS 服务端**三层鉴权模型**：
- `X-API-Key`：识别应用/账号
- `X-OpenViking-Account`：识别账户
- `X-OpenViking-User`：识别 namespace

admin account **只能在 `default` namespace 写盘**——改 `X-OpenViking-User` 想"伪装"成别的用户，**OV 服务端会校验**这条 namespace 是否属于 admin account——`QuanZhiYue` 不属于 → 403。**改 header 不能跨账号**。

**判定铁律**：

1. **admin session 只能写 `default` namespace + `viking://resources/` 公共空间**
2. **写其他 member namespace 需要该成员自己的凭据**
3. **用户说"你可以写到他们 OV 中"**——这是**直觉误解**（按 Windows 文件系统直觉，但 SaaS 多租户架构是按账号隔离的）。**实测确认前不要凭直觉开干**
4. **fallback 方案**：admin session 写公共空间，让 recall 跨 namespace 共享——实际效果基本等价

**实测验证姿势**：

```bash
export $(grep -v '^#' ~/.hermes/.env | grep OPENVIKING_)

# admin 写 default namespace（必成功）
curl -s -X POST "$OPENVIKING_ENDPOINT/api/v1/resources/temp_upload" \
  -H "X-API-Key: $OPENVIKING_API_KEY" \
  -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
  -H "X-OpenViking-User: default" \
  -F "file=@C:/Users/HMSJ/AppData/Local/Temp/perm_test.md"
# 期待 200 + temp_file_id

# admin 写其他 namespace（必失败——验证权限边界）
curl -s -X POST "$OPENVIKING_ENDPOINT/api/v1/resources" \
  -H "X-API-Key: $OPENVIKING_API_KEY" \
  -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
  -H "X-OpenViking-User: QuanZhiYue" \
  -d '{"temp_file_id":"...","to":"viking://user/QuanZhiYue/resources/test.md"}'
# 期待 403 PERMISSION_DENIED
```

---

## 五、实战数据（2026-09-03 伏妖记项目）

| 类型 | 数量 | 备注 |
|---|---|---|
| forget 旧版事件卡 | ~60+ 张 | 按 URI 列表批量，分 8-10 批 |
| forget 旧版偏好卡 | 11 张 | 全部 |
| forget 旧版实体卡 | 3 张 | 6 张实体卡先看内容 → 3 张陈旧 forget，3 张无价值 |
| forget 铁律 v1 | 1 张 | 已被 v2 取代 |
| forget 合并时旧卡 | ~20 张 | DSH 7 张 + 影视 3 张 + cron 3 张 + Seedance 2 张 + Suno 3 张 + Hermes×DSH 3 张 |
| **forget 合计** | **~100 张** | |
| 新建主卡 | 7 张 | DSH/影视核心导向/cron/Seedance/Suno/剧本库/v2.1.x 时间线 |
| 新建 profile | 6 张 | 全志越/施文皓/杨璇/妖玉/叶子/坌子 |
| **新增合计** | **13 张** | |

**单次会话最大规模的 OV 内容整改**。

---

## 六、相关参考

- `references/ov-saas-smoke-test.md` — OV SaaS 写盘基础协议（auth/temp_upload/resources 端点）
- `references/project-ov-overview.md` — 项目级 OV 总览文档结构（README/00-12/验证矩阵）
- `references/feishu-ov-write-protocol.md` — 飞书侧 OV 写盘契约 v1
- `hermes-runtime-pitfalls` skill — OV 写盘底层坑（add_resource wait=true 超时、async abstract、viking_search 新旧版权威判定 等）

---

## 七、维护说明

- 本 skill 由 2026-09-03 实战确立，工作流已验证
- 新增/删除/合并策略请同步更新本文件
- 子代理通览报告的模板见 §二第 2 步描述

**作者**：Hermes Agent
**首次确立**：2026-09-03（伏妖记项目 OV 总览落地 + 全栈迁移任务）
