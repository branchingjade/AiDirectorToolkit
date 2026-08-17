# 插件开源发布全流程（channel-sessions v1.4.0 实战，2026-08-08）

从内部插件 → 开源发布的标准路径。以 channel-sessions（Hermes 桌面插件：前端 ESM plugin.js + 后端 FastAPI plugin_api.py）实测验证。

## 1. 发布前审计维度（开源门槛）

| 维度 | 要求 |
|---|---|
| 文档 | README（安装/使用/API/隐私/架构/开发/添加 locale）+ LICENSE + CHANGELOG |
| manifest | author / homepage / repository / license / 版本号统一（manifest 与前端注释一致） |
| 代码质量 | logging 替代 `except: continue` 静默吞错；参数防御（空值/op 白名单）；并发（lark-cli 反查线程池）；版本号统一 |
| 测试 | 前端 selfcheck（import 检查+逻辑冒烟+i18n 键一致性+硬编码中文扫描）+ 后端 pytest（临时 SQLite fixture，不碰真实 state.db） |
| **CSS 类审计** | **插件 className 全部对照 Hermes 编译 CSS 验证**（scripts/audit_plugin_classes.py）——缺失=UI 静默破损，详见 SKILL.md「Tailwind 类存在性审计」节 |
| CI | GitHub Actions：前端 Node selfcheck + 后端 Python pytest |
| 隐私 | 运行时缓存（如 name_cache.json 存 open_id→真名）**绝不入库**，gitignore 排除；README 说明缓存位置与清除方式 |

## 2. 仓库结构（镜像 Hermes 目录约定）

```
channel-sessions/
├── README.md / LICENSE / CHANGELOG.md / .gitignore
├── .github/workflows/ci.yml
├── desktop-plugins/channel-sessions/   # 前端（plugin.js + selfcheck.js）
└── plugins/channel-sessions/dashboard/ # 后端（manifest.json + plugin_api.py + channel_sessions/service.py + tests/）
```

用户克隆后按 README 分别复制到 `~/.hermes/desktop-plugins/` 和 `~/.hermes/plugins/`（Windows: %LOCALAPPDATA%\hermes）。

## 3. CI 配置要点

- 前端：ubuntu-latest + Node22 → `node desktop-plugins/<id>/selfcheck.js`
- 后端：ubuntu-latest + Python3.11 → `pip install pytest hermes-agent`（**PyPI 有 hermes-agent 包，CI 不需要本地源码**）→ `cd plugins/<id>/dashboard && python -m pytest tests/ -v`
- selfcheck.js 的 i18n 字典提取边界用 `src.indexOf('// 注释锚点')`——**删代码里的锚点注释必须同步改 selfcheck**（v1.4.1 教训：删了 `// 模块级 t` 注释后 selfcheck 直接 SyntaxError）

## 4. 发布步骤（gh CLI，branchingjade 账号实测）

```bash
# 1. 独立 git 仓库（主工作区 .gitignore 加一行排除）
git init -b main && git add -A && git commit -m "feat: ..."

# 2. 建远程仓（--source=. 自动设 origin）
gh repo create <owner>/<name> --public --source=. --remote=origin --description "..."

# 3. 推送
git push -u origin main

# 4. tag + release
git tag v1.4.0 && git push origin v1.4.0
# notes 文件必须写 Windows 路径（gh 是 Windows 程序，读不到 MSYS /tmp）
gh release create v1.4.0 --title "Channel Sessions v1.4.0 — 开源首发" --notes-file release-notes.md
```

## 5. 验证清单（发布后逐项确认）

- [ ] `git ls-remote --tags origin | grep vX.Y.Z` — tag 已推送
- [ ] `gh release view vX.Y.Z --json tagName,isDraft` — release 存在且非 draft
- [ ] `git ls-files | grep -i "name_cache\|pycache\|\.pyc"` — 无隐私/缓存文件入库
- [ ] 本地运行时文件（AppData）与仓库正本 diff 一致（`diff <(git show HEAD:path) localpath`）
- [ ] `gh run list` — CI 在远程真实跑通（不是只看本地绿）
- [ ] 主工作区 `.gitignore` 加入新独立仓库

## 6. 坑汇总

1. **复制文件时隐私数据混入**：`cp -r` 会把运行时生成的 `data/name_cache.json`（真实 open_id→真名映射）和 `__pycache__` 一起拷进仓库——复制后立即清理 + .gitignore 排除。
2. **selfcheck 边界注释**：见上文 §3。
3. **README 截图占位**：写 `![screenshot placeholder](docs/screenshot.png)` 并注明待替换，避免 README 缺图。
4. **版本号三处一致**：manifest.json / plugin.js 头注释 / CHANGELOG——改一处漏两处会漂移。
5. **发布 ≠ 用户验收通过（v1.4.2 教训）**：v1.4.1 发布后用户实测发现「不能直接看会话内容」「没有重命名/删除」——根因是 CSS 类缺失（UI 静默破损）和 hover 隐藏按钮。发布前审计维度必须含 CSS 类存在性验证；破坏性/管理操作按钮默认常显。
6. **块注释 `*/` 提前闭合 = 发布炸弹（v1.4.2 二次教训）**：改 plugin.js 头注释时写「`--ui-fill-*/字号`」——`*/` 在块注释中间终止注释，整个文件语法崩溃、插件加载失败。发布前必须 `node --check` 验证 ESM 语法（cp 到 `$LOCALAPPDATA/Temp` 再查，MSYS /tmp node 读不到）。
7. **发布前记得同步本地运行时**：仓库侧改注释/版本号后，`/bin/cp` 回 AppData 运行时文件，否则 diff 检查不一致（v1.4.2 曾遗留仅注释差异）。

## 7. 管理模型变更发布（v1.4.3 实战）

用户明确「改列表显示即可，分类管理分类筛选/批量赋值/删除分类，**不删会话**，只做前端」——管理模型变更时：

- **移除危险端点是发布的一部分**：删前端调用（ObjectRow trash 按钮、bulkDeleteMut）时，必须同步删后端 `POST /delete-by-object` 路由 + `delete_by_object` + 不再使用的 `_object_key` 函数（留死代码会被 review 抓）。删后端后 pytest 仍过、路由数从 8→7。
- **纯前端功能（重命名显示名/批量赋分类）零后端改动**：ctx.storage 存 `displayOverrides` + 现有 `sessionCats` 复用，`objectLabel(s, t, overrides)` 加第三参——改函数签名要同步所有调用点（buildFilterOptions/SessionRow/详情头部），selfcheck 的 `new Function` 提取逻辑区要更新用例。
- **`.gitattributes` 行尾归一化**：Windows 开发 + GitHub 发布，仓库侧 LF 工作区 CRLF 导致 `diff <(git show HEAD:file) localfile` 整文件假差异。加 `.gitattributes`（`* text=auto` + `*.js/*.py/*.json/*.md text eol=lf`）后 git 自动转换；验证一致性时先 `tr -d '\r'` 再 diff，排除行尾噪音。
- **i18n 新键占位符三连坑**：批量/计数类文案写成 `'Assigned to {n} sessions'` 字符串占位符——SDK render() 不替换 `{n}`，必须写 `n => \`Assigned to ${n} sessions\`` 函数形式（v1.4.1 已踩过一次，v1.4.3 又踩，两处新键都中招）。
- **codicon 名先验证再写**：`tag-add`/`checklist`/`circle-outline`/`tag` 存在，`check-circle-filled` 不存在——用 `grep -o "codicon-<name>" dist/assets/index-*.css` 确认，别想当然。

