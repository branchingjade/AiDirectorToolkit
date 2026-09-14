---
name: attendance-system
description: "用 Hermes 搭建轻量考勤系统——成员库+请假录入+月报 cron 自动投递。触发词：考勤、请假、月报、出勤。"
version: 1.0.0
tags: [attendance, cron, feishu, ops, monthly-report]
---

# 考勤系统搭建与运营（Hermes + cron + IM）

> 用 Hermes 自身能力搭一个「轻量级企业考勤系统」：手动录入请假数据、cron 定时生成月报、自动投递到指定 DM。
> 本 skill 覆盖从「零搭建」到「长期运营」的完整链路，含本机数据库 schema、CLI 工具脚本、cron 模板、报表生成、跨平台投递模式。

## 适用场景

- 中小团队（≤ 30 人）需要打卡/请假统计，但不想采购专业 HR SaaS
- 数据源由用户口述驱动（不是 IM 打卡 API 自动拉）
- 月度报表投递到指定 DM（不是全员群）
- 用 cron + SQLite 实现「无外部依赖」

## 不适用场景

- 大团队（> 100 人）/ 跨地域 / 多班次 → 买专业 SaaS
- 数据源是 IM 打卡 API 自动拉取（钉钉/企业微信考勤 API）→ 直接读 API，本 skill 不写
- 法律合规要求审计追踪 → 本 skill 无审计日志，不满足合规

## 1. 数据架构（SQLite 模板）

数据库位置：`~/AppData/Local/hermes/cron/attendance.db`（Windows 默认）

```sql
-- 人员表（在职/离职状态）
CREATE TABLE members (
    open_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT DEFAULT '在职',
    joined_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 单日状态（手动标记）
CREATE TABLE daily_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    open_id TEXT NOT NULL,
    work_date TEXT NOT NULL,
    status TEXT NOT NULL,              -- 在岗/迟到/早退/请假/缺勤/休息
    note TEXT,
    recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(open_id, work_date)
);

-- 请假记录（多日请假一条记录）
CREATE TABLE leave_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    open_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    leave_type TEXT NOT NULL,          -- 事假/病假/年假/调休/婚假/产假/其他
    reason TEXT,
    recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 月度报表归档
CREATE TABLE monthly_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_month TEXT NOT NULL,
    generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    delivered_at TEXT,
    delivered_to TEXT,
    report_content TEXT,
    UNIQUE(year_month)
);

CREATE INDEX idx_daily_status_date ON daily_status(work_date);
CREATE INDEX idx_leave_records_dates ON leave_records(start_date, end_date);
```

## 2. CLI 工具脚本

`scripts/attendance_cli.py` —— 6 个子命令：add_leave / add_status / list_leave / delete_leave / list_members / gen_report

调用模板：
```bash
'/c/Users/HMSJ/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' \
  'C:/Users/HMSJ/Documents/Hermes/scripts/attendance_cli.py' \
  add_leave --name "魏宁馨" --date "2026-09-05" --type "事假" --reason "看牙医"

'/c/Users/HMSJ/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' \
  'C:/Users/HMSJ/Documents/Hermes/scripts/attendance_cli.py' \
  add_leave --name "杨璇" --date "2026-09-10" --end-date "2026-09-12" --type "病假"
```

**字段验证**：日期格式 YYYY-MM-DD、leave_type 必须在白名单、name 必须能在 members 表查到。

## 3. 用户口述→自动录入（对话意图识别）

用户 DM bot 的话术模式（**关键**——这是手动录入而非 API 拉取的入口）：

| 用户说 | bot 解析后调 |
|--------|---------------|
| `魏宁馨 9月5号 请事假 看牙医` | `add_leave --name "魏宁馨" --date "YYYY-09-05" --type "事假" --reason "看牙医"` |
| `杨璇 9月10-12号 病假 感冒发烧` | `add_leave --name "杨璇" --date "YYYY-09-10" --end-date "YYYY-09-12" --type "病假" --reason "感冒发烧"` |
| `苑津铭 9月8号 迟到 路上堵车` | `add_status --name "苑津铭" --date "YYYY-09-08" --status "迟到" --note "路上堵车"` |
| `录错了 删除 leave_id=3` | `delete_leave --id 3` |

**解析要点**：
- 名字用 members.name 精确匹配，匹配不到则拒录（不猜测拼音/简写）
- 日期模糊时问用户（不补全跨月）
- leave_type 模糊时给候选菜单（不强行 default）
- type 词不在白名单 → 列白名单让用户重选

## 4. cron 调度（每月 1 号 08:30）

```bash
hermes cronjob create \
  --name "月度考勤报表推送" \
  --schedule "30 8 1 * *" \
  --prompt "$(cat <<'EOF'
你是 Hermes 考勤报表 agent。每月 1 号 08:30 由 cron 触发。

【任务】执行考勤报表生成与投递：
'/c/Users/HMSJ/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' \
  'C:/Users/HMSJ/Documents/Hermes/scripts/attendance_report_cron.py'

【收件人】<预设 chat_id，从 setup 时记录>，由脚本内置 lark-cli im +messages-send 直接发送。

【自检】①脚本 exit code 0；②飞书 ok: true (identity=bot)；③数据库 monthly_reports.delivered_at 更新。

【节假日】不过滤（用户偏好：维护类不排除节假日，工作类才走 cn_holiday 三态）。
EOF
)" \
  --deliver local
```

**时间冲突兜底**：用户其他 cron 已经在 08:30 / 09:00 时段（如日报/周报），考勤 cron 排在不同分钟避免资源竞争。本次实战设 `30 8 1 * *`（08:30），与日报 cron 错开。

## 5. 报表投递（IM 通道选择）

### 5.1 飞书 DM 投递模式

```python
# 落盘存档
archive_path = OUTPUT_DIR / f"attendance-{year_month}.md"
archive_path.write_text(content, encoding="utf-8")

# 飞书消息（--as bot 铁律）
subprocess.run([
    "lark-cli", "im", "+messages-send",
    "--chat-id", RECIPIENT_DM_CHAT_ID,
    "--markdown", message,
    "--as", "bot"
])
```

### 5.2 关键决策：发到哪个会话

| 选项 | 何时用 |
|------|--------|
| **指定用户的 DM** (`--chat-id oc_xxx` 或 `--user-id ou_xxx`) | 用户拍板「发给 X」 |
| **全员群** (`--chat-id <group_id>`) | 公开通报场景 |
| **当前会话** | 仅当用户明说「发这里」 |

**判断点**：用户说「发给我」指**当前会话**；说「发给 X」「发到 X 的会话」指**X 的 chat_id**。混用 = 报表投错地方。

### 5.3 飞书云文档投递模式（备选）

如果报表太长不适合 markdown 消息（如 100+ 行表格），走 `lark-cli docs +create`：

1. 生成 markdown 文件
2. `lark-cli docs +create --doc-format markdown --title "..." --content @file.md --as bot`
3. `lark-cli drive +member-add --token <doc_id> --type docx --member-type openid --member-id <user_ou> --perm view --as bot --yes`（**必须显式开权限**，bot 创建的 Doc 默认仅 owner 可看）
4. `lark-cli im +messages-send --user-id <user_ou> --markdown "<简介 + 链接>" --as bot`

## 6. 测试与回归（关键避坑）

### 6.1 测试数据清理

**录入测试数据时用 `--dry-run` 或事后立刻 `delete_leave --id N`**——测试假数据留在生产数据库里会污染次月报表。

### 6.2 cron 第一次触发前必须做

- [ ] DB 已建 + members 表已 seed
- [ ] 至少插入 1 条真实请假 → dry-run gen_report → 确认格式正确
- [ ] bot 身份手动执行报表脚本一次（不发飞书），看 markdown 输出
- [ ] bot 身份手动执行报表脚本一次（真发飞书），验证消息回执 `ok: true`
- [ ] 数据库 `monthly_reports.delivered_at` 字段被更新
- [ ] 删除测试数据，**不留测试痕迹**

### 6.3 月度 cron 触发后必查

- [ ] `monthly_reports` 表新增一行，`delivered_at` 非空
- [ ] 收件人 DM 真收到消息（read-back `im +messages-mget`）
- [ ] 落盘 markdown 归档存在

## 7. 实战 Pitfalls（已踩）

### P1：人员 open_id 反查命中「用户+N」脱敏名 ≠ 该用户离职

bot `+get-user --user-id <ou>` 返回 `name: "用户133976"` 时——**先判定是资料问题不是离职**。判定链：①同群其他成员 bot 全部正常，唯独此人「用户+N」→ 非全局权限问题；②user 身份 `+search-user` 返回 `localized_name` 有真名 → 字段差异实锤。**修复**：让该用户补全飞书姓名资料；脚本对「用户+N」降级显示原名（不误标）。

### P2：两个不同人共享同一种「用户+N」模式时不可凭直觉归并

本次实战中我把 `ou_7c8f...` 当成「叶子」开除，结果她就是杨璇在职。**判定铁律**：①「离职」是 admin 拍板的事实，不是记忆里的模糊说法；②确认离职前**先问用户不要猜**；③如果用户说「A ≠ B 是两个人」，立刻更新画像/记忆的反面教材区。

### P3：cron 时间设错时立即 update（不要删了重建）

`hermes cronjob update <job_id> --schedule "..."` 比「remove + create」更稳——保留 job_id、prompt 历史、route 表关联。错就改，不要全套重来。

### P4：bot 创建的飞书云文档默认仅 owner 可看

不显式 `drive +member-add --perm view`，收件人点开会「无权限」。bot 创建的 Doc 默认 full_access 只给 bot 自己 + 当前 CLI user。必须再跑 `drive +member-add` 才能让目标用户访问。**飞书云文档权限模型是「显式 ACL」不是「链接即访问」**。

### P5：lark-cli commands 在 Windows bash 里要走 `lark-cli`（不加 .exe）

git-bash MSYS 路径转换对 lark-cli 自身不生效，但对其参数里的 Windows 路径生效（路径走单引号，禁 `~` 与反斜杠）。本次踩坑：`/c/.../_feishu_jian_archive.md` 必须写 Windows 风格 `C:/...`，否则 git-bash 报错。

## 8. 跨平台适配

| 平台 | 投递命令 | 文档命令 |
|------|---------|---------|
| 飞书 | `lark-cli im +messages-send --chat-id oc_xxx --markdown "..." --as bot` | `lark-cli docs +create --doc-format markdown --title "..." --content @file.md --as bot` |
| 钉钉 | `curl -X POST https://oapi.dingtalk.com/robot/send?access_token=...` | 钉钉文档 API 略 |
| 企业微信 | 企微 webhook + markdown 消息 | 企微文档 API 略 |
| Slack | `slack-cli chat write --channel #xxx --text "..."` | n/a |

**通用约束**：①投递身份 = bot 身份（不冒充 admin）；②内容带 markdown 但避开各平台不支持的语法。

## 9. 长期维护

- 每月 1 号 cron 触发后，留意飞书消息回执——如果连续 2 个月没回执，**立刻**手动 `lark-cli im +messages-send --dry-run` 测 token 有效性
- 人员变动（入职/离职）→ 更新 `members` 表 + 通知 admin 拍板画像更新
- 跨年归档：每年 12 月报表生成后，把 `attendance.db` 备份到 `cron/_archive/attendance/<YYYY>/` 再清空
- 报表格式迭代 → 改 `attendance_report_cron.py` 的 `gen_markdown_report()` 函数，不要动 `attendance_cli.py`

## References

- `references/setup-walkthrough.md` —— 从零搭建 7 步完整 walkthrough（含本次实战路径与所有命令）
- `templates/attendance_cli.py` —— CLI 工具模板（已含 6 个子命令）
- `templates/attendance_report_cron.py` —— 报表生成 + 投递脚本模板
- `scripts/init_attendance_db.py` —— DB 初始化 + 种子数据脚本

## 与现有 skill 的关系

- **feishu-multi-user-collab**（user-owned）：本 skill 是其「考勤运营」垂直应用，人员管理复用它的 §2 成员画像 + §6 健康检查
- **hermes-runtime-pitfalls**（user-owned）：P1/P2 人员状态判断复用其「用户+N 根因判断」节
- **publish-to-feishu**：本 skill 的「飞书云文档投递模式」是其精简版，专注考勤场景
- **cron-ops / cron-monitor**：本 skill 的 cron 调度复用其节假日策略