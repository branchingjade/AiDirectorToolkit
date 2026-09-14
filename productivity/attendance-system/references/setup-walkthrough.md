# 从零搭建考勤系统 —— 7 步 Walkthrough

> 本文档基于 2026-09-03 「所有人开工」群 10 人 + 飞书 DM 月报实战路径。
> 严格按顺序执行，每步都有「验证命令」。

## 第 1 步：核实群 chat_id + 人员名单

```bash
# 查群（关键字搜索）
lark-cli im +chat-search --query "开工" --as bot

# 列全部群（备用）
lark-cli im +chat-list --types group --as bot

# 拉群成员
lark-cli im +chat-members-list --chat-id "<oc_xxx>" --page-all --as bot
```

**验证**：返回 `user_total=N` + 每条 `{member_id: ou_xxx, name: "..."}`。

**踩坑**：bot `+get-user` 返回 `name: "用户133976"` 不代表该用户离职——是飞书资料字段缺失。先用 `user +search-user --user-ids <ou>` 查 `localized_name`，有真名说明人是该人在职。

## 第 2 步：核实报表接收人 DM chat_id

```bash
# 直接 user-id 发 DM（不需要 chat_id）
lark-cli im +messages-send --user-id "<ou_xxx>" --markdown "<测试>" --as bot
# 返回 data.chat_id 即为该用户的 DM 会话 ID，存下来后续用
```

**实战**：本次报表接收人是魏宁馨 `ou_94566a9aab7dbe27afe38d759e80c534`，她的 DM chat_id 是 `oc_a856f8f1e2fc25c61185ab0191133c00`。

## 第 3 步：建数据库（执行 init 脚本）

```bash
'/c/Users/HMSJ/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' \
  'C:/Users/HMSJ/Documents/Hermes/scripts/init_attendance_db.py'
```

**验证**：
```bash
# 查询全员
'/c/Users/HMSJ/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' \
  'C:/Users/HMSJ/Documents/Hermes/scripts/attendance_cli.py' list_members
```

应输出 N 名在职人员（按字母排序）。

## 第 4 步：测试请假录入与报表生成

```bash
# 录入测试数据（务必事后删除）
python attendance_cli.py add_leave --name "陈星艳" --date "2026-09-03" --type "事假" --reason "测试"

# dry-run 报表
python attendance_report_cron.py --month "2026-09" --dry-run

# 清测试数据
python attendance_cli.py delete_leave --id 1
```

**验证**：dry-run 输出含「请假明细」表格且仅你刚录入的那一条。

## 第 5 步：真实发送一次月报到指定 DM

```bash
# 取消 dry-run，真发
python attendance_report_cron.py --month "2026-09"
```

**验证**：
```bash
# 读回刚才发的那条消息确认
lark-cli im +messages-mget --message-ids "<返回的 message_id>" --as bot
# 应看到 msg_type=post / sender.id_type=app_id / chat_id=oc_a856f8...
```

## 第 6 步：注册 cron（每月 1 号 08:30）

```bash
hermes cronjob create \
  --name "月度考勤报表推送" \
  --schedule "30 8 1 * *" \
  --prompt "$(cat <<'EOF'
你是 Hermes 考勤报表 agent。每月 1 号 08:30 由 cron 触发。

【任务】执行考勤报表生成与投递：
'/c/Users/HMSJ/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' \
  'C:/Users/HMSJ/Documents/Hermes/scripts/attendance_report_cron.py'

【收件人】<你的报表接收人 DM chat_id>，已由脚本内置 lark-cli im +messages-send 直接发送。

【必要自检】
1. 报表脚本必须返回 exit code 0
2. 飞书消息必须返回 ok: true（identity = bot）
3. 数据库 monthly_reports.delivered_at 必须更新到当前时间

【异常处理】
- 脚本失败：报告错误（不要尝试重发，避免重复投递）
- 飞书 API 失败：报告错误，附 stderr 完整内容
- 节假日：不过滤（用户偏好——维护类与个人 cron 不排除节假日），直接跑

【输出】简报：本次报表月份、发送状态、收件人、月度数据（请假人数/请假天数）。
失败时如实报告错误，不要沉默。
EOF
)" \
  --deliver local
```

**验证**：
```bash
hermes cronjob list | grep "月度考勤"
# 应看到 next_run_at = 下个月 1 号 08:30
```

## 第 7 步：长期监控（每月 1 号后）

- 收件人 DM 真收到消息（主动问一句或监控 monthly_reports.delivered_at）
- 飞书 token 不过期（lark-cli auth status 周期性检查）
- 人员变动时更新 members 表 + 通知 admin 更新画像

## 完整命令速查

```bash
# 录入
python attendance_cli.py add_leave --name "<姓名>" --date "YYYY-MM-DD" --type "<类型>" --reason "<原因>"
python attendance_cli.py add_leave --name "<姓名>" --date "YYYY-MM-DD" --end-date "YYYY-MM-DD" --type "<类型>"
python attendance_cli.py add_status --name "<姓名>" --date "YYYY-MM-DD" --status "<状态>" --note "<备注>"

# 查询
python attendance_cli.py list_members
python attendance_cli.py list_leave --month "YYYY-MM"

# 修正
python attendance_cli.py delete_leave --id <leave_id>

# 月报
python attendance_report_cron.py                          # 默认上月
python attendance_report_cron.py --month "YYYY-MM"        # 指定月份
python attendance_report_cron.py --dry-run                # 仅生成不发飞书
```