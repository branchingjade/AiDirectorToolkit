# Hermes Cron 投递模式

本次会话建立 Hermes 版本简报 cron job 的过程和教训。

## 模式选择

| 模式 | 适用 | Windows 陷阱 |
|------|------|-------------|
| `no_agent=True` + Python 脚本 | 纯数据收集/看门狗 | **stdout 始终空**——`subprocess.run(capture_output=True)` + `_sanitize_subprocess_env` 在 Windows 上无法捕获 Python 子进程 stdout |
| `no_agent=True` + `.sh` 脚本 | 简单 shell 看门狗 | 需要 Git Bash，Windows cron runner PATH 不包含 |
| `no_agent=False` + LLM 驱动 | 需推理/翻译/格式化 | ✅ 推荐。最终 assistant 回复即投递内容 |

**结论：Windows 上需 LLM 处理的任务一律用 `no_agent=False`。**

## LLM 驱动 Cron Prompt 设计

### 致命陷阱

- **最终回复必须是投递内容**。LLM 会用 write_file 保存状态后回复"已完成"，导致 `response_len=26`，投递内容为空。
- 解决方法：prompt 中明确"你的唯一输出就是简报本身，不要写额外确认"。

### 内容密度调优

迭代了 10+ 次才找到平衡：

| 迭代 | 问题 | 修正 |
|------|------|------|
| 全量翻译 | 太长，易读性差 | 减条目 |
| 6-8 条精选 | 缺关键内容 | 按分类覆盖，每条 10 字解释 |
| 纯文本 | 没排版 | 用 markdown（##、-、**粗体**、> 引用） |
| 整篇 ``` | 全在一代码框 | 分类标题在外面，**更新条目装一个代码块** |
| 建议太泛 | "日常升级即可" 没用 | 指明优先级、具体避坑 |

### 推荐 Prompt 结构

```
你是 X 助手。最终回复就是完整报告，不要额外说明。

步骤：1. 拉取数据 2. 对比状态 3. write_file 更新 4. 最终回复=完整报告

格式规则：
- 更新条目装在一个代码块里（一个 ``` 包裹全部）
- 每条 10 字以内解释
- 升级建议写具体：指明优先级、避坑

输出模板：
## 🆕 v0.17.0 — 主题概括
```
🔴 安全
- 要点：解释

🟡 桌面端
- 要点：解释
```
> 💡 安全修复必升，桌面端体验提升明显，重启网关验证连接。
```

**关键：禁止在代码块外放更新条目，禁止用"已完成"等结束语。**

## 投递配置

### 去除英文包裹
```bash
hermes config set cron.wrap_response false
```

### Feishu DM 投递

**chat_id 格式：用 `oc_` 不用 `ou_`。**

查找方法：
```bash
# 1. 用 lark-cli 以 open_id 发一条测试消息
lark-cli --as bot im +messages-send --user-id ou_7288c4a018284580d463d0239cbd47cf --text "test"

# 2. 返回的 chat_id 就是 DM 的 oc_xxx
# {"chat_id": "oc_58433ce37dc9e6ba6836da36b370fc01", ...}
```

cron job 的 deliver 参数：
```
feishu:oc_58433ce37dc9e6ba6836da36b370fc01
```

### 验证投递

```bash
grep "491b6b1d28f3" ~/AppData/Local/hermes/logs/agent.log | grep "deliver"
# 成功: "delivered to feishu:oc_xxx"
# 静默: "empty stdout — silent run" (no_agent=True 时常见)
# 短响应: 检查 response_len，<50 说明 LLM 没输出报告
```

## 状态文件路径

Windows 上 `~/.hermes/` 和 `$HERMES_HOME`（`~/AppData/Local/hermes/`）是两个不同目录。脚本和 cron prompt 统一用 `~/.hermes/hermes_monitor_last_tag.txt`（cron 运行环境能访问），手动测试从 bash 用同路径。

## 回复渠道原则

- Hermes TUI 里问 → TUI 回复
- 飞书里问 → 飞书回复
- cron 自动推送 → 推飞书
- 不跨渠道

## session_search 陷阱：搜内容，不搜源

**`session_search(query="X")` 用的是 FTS5 全文搜索消息内容，不是 session 的 `source` 元数据字段。**

- `session_search(query="feishu")` → 只匹配消息正文里含"feishu"词条的会话
- 会话的 `source=feishu` 但用户聊的是短剧、剧情、提示词 → 内容不含"feishu" → 永远搜不到
- 后果：cron 摘要报告"无其他用户对话"，但 DB 里明明有几十条会话

**正确做法**：
- **浏览模式**：`session_search()` 不带 query，浏览所有近期会话，再按返回的 `source` 字段手动过滤
- **直接 SQL**：`SELECT * FROM sessions WHERE source='feishu' AND started_at > ...`，不走 FTS
- **宽泛 FTS 查询**：搜高频中文词（"的""了"）而非平台名，但不如上面两种可靠
