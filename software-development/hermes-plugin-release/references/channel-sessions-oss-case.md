# channel-sessions v1.4.0 开源发布实测记录（2026-08-08）

Hermes 渠道会话管理插件（channel-sessions）从功能可用 → 开源发布水平的完整改造实录。本文件是 hermes-plugin-release skill 的实战案例，供未来同类插件改造对照。

## 插件结构（改造前）

- `desktop-plugins/channel-sessions/plugin.js`（649 行，三栏布局：左筛选 | 会话列表 | 消息详情）+ selfcheck.js
- `plugins/channel-sessions/dashboard/manifest.json`（v1.0.0，无 author/repository）
- `plugins/channel-sessions/dashboard/plugin_api.py`（114 行 FastAPI 适配层）
- `plugins/channel-sessions/dashboard/channel_sessions/service.py`（261 行：跨 profile 扫 state.db + 飞书真名反查 + 管理操作代理）
- `channel_sessions/data/name_cache.json`（open_id→真名缓存，TTL 一周）

## 审计发现的问题（按优先级）

| # | 问题 | 修复 |
|---|---|---|
| 1 | `REFRESH_INTERVAL_MS` 定义了但 sessionsQuery 没用 refetchInterval（只 messages 用了）→ 列表不自动刷新 | sessionsQuery 加 `refetchInterval: REFRESH_INTERVAL_MS` |
| 2 | 后端零日志，`except Exception: continue` 静默吞错 | 全量加 `logger.warning/debug` |
| 3 | 真名反查串行（每个 open_id 起子进程 1-2s） | `ThreadPoolExecutor(max_workers=4)` |
| 4 | `_mutate` 里 `kwargs["title"]` 直接索引（API 层有默认但 service 层脆） | 改 `kwargs.get` + 空值校验 + op 白名单 |
| 5 | 版本号漂移：manifest 1.0.0 vs 注释 v1.3 | 统一 v1.4.0，manifest 补 author/homepage/repository/license |
| 6 | `__pycache__` 在目录里 | 发布前清理 + gitignore |
| 7 | UI 全中文硬编码 | i18n 双语字典 68 键 |
| 8 | 无测试无 CI | pytest 21 项 + GitHub Actions |
| 9 | 消息固定 200 条无分页 | 后端 offset + has_more，前端加载更多（前端部分未完成） |

## 测试抓出的真实 bug（重要——测试的价值证明）

1. **is_gateway 漏判 desktop**：`s["source"] not in ("cli", "tui")` 把 desktop 来源标成渠道会话。前端 objectKey 已把 desktop 归为 local，后端判定不一致。修复：加 `"desktop"` 排除。
2. **`_rows_for_db` 打开失败未捕获**：`_open_db_ro` 在 try 块外，坏库（非 SQLite 文件/缺库）会让整个 list_sessions 抛异常。修复：连接打开也包进 try，失败返回 [] + warning 日志。测试用例 `test_rows_for_db_missing_file_returns_empty` 直接复现。

## 关键实测数据点

- **name_cache.json**：12 条缓存，`ou_5373d...` → 苑津铭 等，TTL 一周
- **lark-cli 反查格式**：`contact +get-user --user-id ou_xxx --as bot` 返回 `{"ok":true,"identity":"bot","data":{"user":{"name":"苑津铭",...}}}`——解析用 `(payload.get("data") or {}).get("user") or {}` 防御
- **pytest 环境**：hermes-agent venv 的 python 3.11.15 + pytest 9.1.1；`python -m pip install pytest` 才装进 venv（裸 pip 装到系统 Python）
- **CI 可行性**：hermes-agent 在 PyPI 有 0.19.0，CI 直接 `pip install hermes-agent` 即可 import hermes_state.SessionDB
- **i18n 插值坑**：SDK render() 只认字符串字面量或函数——`'{n}分钟前'` 不替换，必须 `n => \`${n}分钟前\``（apps/desktop/src/i18n/runtime.ts 源码确认）

## 改造后验证结果

- `node selfcheck.js` 全绿：29 import 无未用、11 项逻辑断言、i18n 68 键 en/zh 一致、无硬编码中文残留
- `python -m pytest tests/` 21/21 通过（0.38s）
- `list_sessions(limit=10)` 真实调用正常（10 sessions、1 名字命中缓存）

## 遗留事项（下次会话继续）

1. 前端消息「加载更多」按钮（后端 offset/has_more 已就绪，plugin.js 未接）
2. README.md / LICENSE(MIT) / CHANGELOG.md 未写
3. git init + GitHub 仓库（归属 branchingjade）+ tag + release
4. 桌面 app 热重载确认 i18n 后实际渲染
