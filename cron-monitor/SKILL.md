---
name: cron-monitor
description: "通用定时监控推送框架——采集数据→LLM加工→格式化推送。支持多源配置，飞书推送。所有定时报告类 cron 的统一入口。"
version: 1.1.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, monitor, notification, feishu, release, rss]
---

# Cron Monitor — 通用定时监控推送

所有定时报告类 cron job 的统一规范入口。覆盖 LLM 驱动监控、脚本采集推送、格式约定、渠道规则。

## 现有 Cron 任务

| Job ID | 名称 | 频率 | 类型 | 说明 |
|--------|------|------|------|------|
| `491b6b1d28f3` | Hermes 版本简报 | 周一 9:00 | LLM | 本地 vX → GitHub latest，对比差距 + 中文简报 |
| `e14576c54fcf` | 外部技能同步（统一） | 每天 9:00 | LLM（terminal 调脚本） | 自动发现所有 tap + yaml 配置的源，格式自检测，JSON 输出→LLM 智能判断报告 |
| `7c3df411d075` | 备份 | 每天 8:00 | LLM（terminal 调脚本） | Hermes+Obsidian → 坚果云 WebDAV |
| `d89acf50b8a2` | lark-cli OAuth token 检查+自动续期 | 每天 9:00 | LLM（terminal 调脚本+lark-cli） | 过期前自动触发续期（lark-cli whoami），refresh token 已过期时提醒手动授权 |

全部 LLM 驱动（`no_agent=false`，不配 `script` 字段），推送到飞书 DM。无更新也报告。

## 快速开始（新增监控源）

**方式一：加进 sources.yaml**（适合 GitHub Releases / RSS / API）
1. 编辑 `~/.hermes/hermes_monitor_sources.yaml`
2. 按模板加一条源
3. state 文件自动管理（`~/.hermes/hermes_monitor_<name>.txt`）

**方式二：脚本采集 + LLM 格式化**（适合复杂采集逻辑）
1. 写脚本采集数据→print 到 stdout
2. 创建 cron job，prompt：`用 terminal 执行 <脚本>，读取输出格式化为中文简报作为最终回复。`
3. 脚本存 `~/.hermes/scripts/`

## 监控源配置（sources.yaml）

```yaml
sources:
  - name: hermes-agent           # 唯一标识
    type: github-release         # github-release | rss | custom-command
    repo: NousResearch/hermes-agent
    enabled: true
    llm_level: 3                 # 1=纯翻译 2=+解释 3=+评级+建议
    include_categories:          # 只报告这些分类
      - security
      - windows
      - desktop
      - cli
      - tools
      - core
    exclude_keywords:            # 过滤关键词
      - discord
      - slack
      - docker
    max_items: 2                 # 每分类最多条数
```

## 输出格式约定

**LLM 驱动格式：**
```
## 🆕 v0.17.0 — 覆盖范围大扩展
一句话概括。

[一个 ``` 代码块包裹所有更新条目，分类+emoji+评级]

> 💡 升级建议：具体、指明优先级
```

**格式要点（来自调试实战）：**
- 更新条目放一个 ``` 内，标题和概述在外面
- 每条解释 10 字以内
- 评级 🔴🟡⚪ 在码块内生效
- 6-8 条覆盖全部分类
- 升级建议写具体：优先级、避坑

## 通用公约

1. **中文输出**：不允许英文。`cron.wrap_response: false` 必须设
2. **LLM prompt 关键句**："最终回复就是简报正文，不要工具调用，不要结束语"
3. **变更报告**：对比上次状态，报告增量
4. **无变更也要报告**：即使没有新内容，也要输出简洁状态（如"无更新""已是最新"）。用户不想猜"是没跑还是没变化"
5. **渠道规则**：cron 自动推→飞书；Hermes TUI 手动问→TUI 回。不跨渠道
6. **自检清单**：新增/修改后必须 `cronjob run` 验证

## LLM 加工级别

| 级别 | 做什么 |
|------|--------|
| 1 | 纯翻译 英→中 |
| 2 | + 解释对用户的影响 |
| 3 | + 评级（🔴🟡⚪）+ 升级建议 |

## 陷阱

- **LLM 输出陷阱**：deepseek 容易把报告写入文件（response_len=26→"已完成"）而非最终文本。prompt 必须写"最终回复就是简报正文，不要工具调用，不要结束语"
- **LLM 静默陷阱**：LLM 只调工具不输出文本→cron 视为 [SILENT] 不投递。必须引导 LLM 把报告作为最终回复
- **`***` 写入陷阱**：memory 中 masked 的凭据（`***`）会被 `write_file` 当成字面文本写入 Python 字符串，导致语法错误。脚本里凭据用 `startswith("PREFIX=")` 匹配，禁止包含 `***`
- **cron.wrap_response**：必须 false，否则英文 "Cronjob Response" 头尾污染
- **格式平衡**：整篇塞 ```→代码块、无码块→纯文本。正确：标题在外+一个码块包裹条目
- **HERMES_CRON_TIMEOUT**：cron job 的 inactivity 超时，默认 600s。**但这不是根因修复的优先选项**——如果已配置 fallback_providers，正确做法是给主 provider 配短 `request_timeout_seconds`（如 `hermes config set providers.deepseek.request_timeout_seconds 120`），让挂起请求快速失败→触发重试→切兜底模型。若只调大 cron 超时，API 挂起仍会干等（SDK 默认 600s read timeout 与 cron 600s inactivity 恰好相等，cron 先杀 job，兜底链永远不触发）
- **兜底模型不生效的诊断**：fallback 只在 API 明确报错（429/5xx/空响应）时触发；请求**挂起不返回**（`waiting for non-streaming API response` + `idle for 600s` 超时）时兜底链不触发。根因是 provider 未配 request_timeout_seconds。改 config.yaml 受保护，必须用 `hermes config set providers.<name>.request_timeout_seconds <秒>`，写 .env 也受保护
- **手动 vs 定时**：Windows 上 manual `cronjob run` 无法捕获 LLM 最终回复（SILENT），但定时触发正常。测试只能用定时触发或 lark-cli 直推
- **飞书 DM chat_id**：用 `lark-cli --as bot im +messages-send --user-id ou_xxx --text "..."` 测试可获取 oc_ 格式 chat_id
- **首次运行**：无 state 文件→全量报告。手动初始化 state 为最新值
- **版本对比对象**：对比本地安装版本（`hermes --version`），不是 last-seen tag。本地 vX 对比 GitHub latest→报告差距
- **LLM 驱动禁 script 字段**：`no_agent=false` + `script` 字段时 cron 先跑脚本→Windows 上 stdout 丢失→SILENT。正确做法：不配 `script`，让 LLM 自己 `terminal` 执行脚本
- **渠道不跨**：TUI 问→TUI 回，飞书问→飞书回，cron→飞书
- **HERMES_HOME 路径**：手动测试用 `~/.hermes/`，cron 用 `AppData/Local/hermes/`。脚本内优先读 `HERMES_HOME` 环境变量，fallback 检查两个路径
- **凭据读取**：cron 子进程 env 被 sanitize，脚本不能靠 `os.environ` 读飞书密钥。必须从 `.env` 文件直接 `startswith("FEISHU_APP_ID=")` 匹配
- **版本检查方式**：首选 `git -C ~/AppData/Local/hermes/hermes-agent log HEAD..origin/main` 显示本地真正缺少的提交。但 repo 是 shallow clone（depth=1）时只显示顶层合并提交，不显示具体功能提交——需 fallback 到 GitHub Compare API：`curl -s "https://api.github.com/repos/NousResearch/hermes-agent/compare/<old_sha>...<new_sha>"` → 解析 `total_commits` 和 `commits[].commit.message` 获取完整列表。`old_sha` 从 fetch 输出 `1c4cc00f7..5445e42b8` 提取前半段
- **`hermes --version` 格式**：输出含 `upstream <sha> · local <sha> (+N carried commit)`，需解析出 N 为落后提交数
- **shallow clone 陷阱**：Hermes Agent 仓库是 shallow clone（depth=1），`git log HEAD..origin/main` 只显示顶层合并提交。验证：`git rev-list --count HEAD` 返回 1。需用 GitHub Compare API 获取完整提交列表，或先 `git fetch --unshallow`（耗时较长）
