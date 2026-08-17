---
name: hermes-plugin-release
description: "Hermes 桌面插件开源发布/工程化。触发词：插件开源、插件发布、达到开源水平。"
version: 1.0.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [hermes, plugins, release, opensource, i18n, testing]
    category: software-development
    related_skills: [hermes-desktop-plugin-dev, hermes-desktop-plugins, hermes-session-management]
---

# Hermes 桌面插件开源发布 / 工程化

把 Hermes 桌面插件从「能用的功能」提升到「可开源发布的工程品」。适用于：插件要发 GitHub、用户要求「达到开源发布水平」、或插件功能已全但缺工程面（测试/文档/i18n/CI）。与 hermes-desktop-plugin-dev（本机架构与坑）互补——本 skill 管发布级工程化。

## 插件双目录结构（前置认知）

- 前端：`desktop-plugins/<id>/plugin.js`（纯 ESM，jsx()/jsxs()，无构建）
- 后端：`plugins/<id>/dashboard/`（manifest.json 的 `"api": "plugin_api.py"` + 业务包 + tests/）
- 两处都要部署，config.yaml `plugins.enabled` 需含插件 id
- ⚠️ 版本号三处统一：manifest.json + plugin.js 头注释 + CHANGELOG（曾出现 manifest 1.0.0 vs 注释 v1.3 漂移）

## 开源发布清单（按优先级）

### P0 门槛（缺了不算开源）
1. README.md：安装（双目录复制 + config 启用）、截图、使用说明、API 文档、隐私说明（如 name_cache.json 存 open_id→真名映射这类敏感缓存必须披露）
2. LICENSE（选型让用户拍板；插件生态默认 MIT）
3. CHANGELOG.md
4. manifest 元数据：author / homepage / repository / license

### P1 代码质量（review 会被抓）
5. 后端零日志 = 不可排查：`except: continue` 全部替换为 `logger.warning`（保留静默语义但留痕）
6. 慢外部调用并发化：子进程反查等 I/O 密集用 `ThreadPoolExecutor`（限 max_workers 防限流，如 lark-cli 5 QPS）
7. service 层防御：参数空值校验、op 白名单、`kwargs.get` 兜底——API 层有默认值 ≠ service 层安全
8. 发布前清 `__pycache__` + 加 .gitignore

### P2 发布水平
9. i18n（见下）
10. pytest 测试（见下）
11. CI（见下）
12. 前端增强：列表自动刷新（refetchInterval，别定义常量忘了用）、分页加载更多、错误提示区分前后端

## i18n 关键坑（SDK 源码实测）

`ctx.i18n.register({ en, zh })`（register 时调用）+ 组件内 `usePluginI18n(id)`（响应式）；handler/store 用 `ctx.i18n.t`（非响应式）。

⚠️ **插值只能用函数形式**：SDK 的 `render()` 只支持字符串字面量或函数 `(...args)=>string`，`'{n}分钟前'` 这类占位符**不会替换**，会原样输出（plugin-i18n.ts / runtime.ts 源码确认）。带参文案必须写 `n => \`${n}分钟前\``。

- en/zh 键集合必须一致——selfcheck 加「键集合 diff」检查
- 模块级纯函数（fmtTime/platformLabel/objectLabel 等）拿不到响应式 t：改成接受 `t` 参数由组件注入；组件内 `usePluginI18n` 拿 t 逐层传
- 平台名等专名放静态映射（Feishu/WeChat），界面文案进字典
- 校验：selfcheck 扫字典区之外的中文残留（正则 `[\u4e00-\u9fff]{2,}`）

## 后端测试模式（pytest）

- 临时 SQLite fixture 建 sessions 表，**列名与真实 state.db 对齐**（sessions 用 started_at 非 created_at、messages 用 timestamp）
- monkeypatch `_profile_dbs` 返回 [(profile, tmp_db)]；monkeypatch 反查函数避免真实子进程
- 用例必须有：坏库/缺库（`_rows_for_db` 打开失败要返回 [] 不拖垮整体）、子会话过滤（parent_session_id 非空）、is_gateway 判定、查询列与前端期望字段一致
- 实测收益：is_gateway 漏判 desktop 来源、`_rows_for_db` 打开失败未捕获——都是测试抓出来的真实 bug

## CI 模式

```yaml
frontend: actions/setup-node@v4 (22) → node desktop-plugins/<id>/selfcheck.js
backend:  actions/setup-python@v5 (3.11) → pip install pytest hermes-agent → cd plugins/<id>/dashboard && python -m pytest tests/
```
hermes-agent 在 PyPI 有发布（0.19.x），CI 直接 pip install，不用 checkout 源码。仓库布局镜像 Hermes 目录约定（desktop-plugins/ + plugins/ 两个子目录），用户可整目录拷贝到 $HERMES_HOME。

## selfcheck.js 模式（前端冒烟）

1. import 未使用检查（正则提取 import 块 + 正文 `\bname\b` grep）
2. `new Function(logicSrc + '; return {...}')` 提取工具函数区做纯逻辑断言（t 用 `key=>key` mock）
3. i18n 键集合 en/zh 一致
4. 硬编码中文残留扫描（排除注释/字典区）
5. **工具函数签名改了（如加 t 参数）必须同步更新 selfcheck 用例**——签名一变 selfcheck 先炸，这是第一道防线

## 分页加载更多

`SessionDB.get_messages(session_id, limit, offset)` 原生支持 offset 分页（插入序，offset 需配 limit）。后端返回 `has_more`（多查一条 `offset+limit` 探测），前端维护 offset 状态 + 「加载更多」按钮。

## Pitfalls

- **plugin.js 的 lint 报错是假警报**：patch/write_file 工具的 node check_syntax 对 ESM 插件文件报 `MODULE_NOT_FOUND`（CJS loader 跑不了 ESM），属预期——判断改动有效看 diff 和 selfcheck 结果，不看这个 lint
- pytest 收集 vs 直接 python -c 行为不同：脚本内 `sys.path.insert` 的路径要算对（`Path(__file__).parent.parent` 已是 dashboard 目录，别再拼一层 `dashboard/`——曾因多拼一层 pytest 报 ModuleNotFoundError 而 python -c 正常）
- venv 装包用 `python -m pip install`，裸 `pip` 可能装到系统 Python（Windows 上 which python 与 which pip 指向不同解释器时先核对）
- 打开完整会话路由：`sessionRoute(id)` = `'/' + encodeURIComponent(id)`（SESSION_ROUTE_PREFIX='/'，routes.ts 确认）
- 后端反查外部 CLI 的 JSON 结构先实测一次再写解析（如 lark-cli contact +get-user 返回 `data.user.name`，`payload.get("data") or {}` 防御）

## 验证清单

- [ ] node selfcheck.js 全绿（import 无未用 + 逻辑断言 + i18n 键一致 + 无硬编码中文）
- [ ] pytest 全过
- [ ] manifest 版本 = plugin.js 注释版本 = CHANGELOG 版本
- [ ] 桌面 app 热重载后无报错 toast（Settings → Plugins → Reload desktop plugins）

## 相关文件

- 案例实测（channel-sessions v1.4.0 全流程）：references/channel-sessions-oss-case.md
- 官方 SDK 参考：hermes-desktop-plugins skill（bundled，templates/plugin.js）
