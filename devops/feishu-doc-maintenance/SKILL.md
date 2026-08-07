---
name: feishu-doc-maintenance
description: 飞书文档批量维护：格式修复、内容校验、bot创建与权限、富功能优化。触发词：飞书格式修复、批量改文档。
---

# 飞书文档批量维护

批量编辑/修复/优化飞书文档的实战工作流。lark-cli 官方 skill（lark-doc/lark-drive/lark-shared）管命令语法，本 skill 管「实际怎么跑」——批量执行模式、验证陷阱、权限开通、富功能落地。适用于：整篇文档格式统一、标题层级修复、bot 身份建文档、加时间轴/callout 优化。

## 一、批量格式修复（block_replace 模式）

适用：整篇文档的标题层级统一（h2/h3/h4 混乱）、伪居中空格清理、误标标题还原、人物行统一。

**流程**：
1. `docs +fetch --detail with-ids` 拉全文 XML 存档
2. Python 正则**先诊断再生成**修复清单 `{block_id, old, new_xml}`——诊断阶段必须枚举所有格式变体（普通段、加粗段、嵌套标签、伪居中空格等），正则覆盖不全=漏网
3. 生成 bash 脚本逐个 `block_replace`（**lark-cli 在 Windows 是 shell 命令，Python subprocess 调用报 WinError 2，必须用 bash 循环**）
4. 每轮执行完**重新 fetch**，用新 XML 重新生成清单——`block_replace` 后旧 block ID 失效，已完成项自动跳过。**分轮执行，每轮基于最新状态**

**关键规则**：
- `block_replace` 会替换块并**改变 block ID**：每轮操作后必须重新 fetch，不要复用旧 ID
- 同一 block 只能 replace 一次；内容相同的替换会报 `result: failed`（no document changes）——不代表失败，是已生效
- 命令输出可能带 `Deleting.../Moving...` 前缀行，JSON 解析要容错（找 `"ok": true` 或取最后一段），不要因解析失败误判操作失败

## 二、验证陷阱（嵌套标签正则）

**坑**：用 `<h4[^>]*>([^<]{0,30})</h4>` 这类正则扫描标题块，**遇到嵌套 `<b>` 标签会漏检**——如 `<h4><b>人物</b>：陆老邪</h4>` 的内容含 `<`，`[^<]` 匹配失败，导致「0 残留」误报，实际有漏网。

**正确写法**：`<(h[1-4])([^>]*)>(.*?)</\1>` + `re.S` 标志，再对捕获的 inner 去标签取纯文本判断。**所有验证脚本必须用这个安全正则，不能图省事用 `[^<]`。**

## 三、内容零改动验证

改格式必须证明内容没动（用户红线）：
- 修复前 XML 存档 vs 修复后 XML，都转纯文本（`re.sub(r'<[^>]+>','')` + 去空白）逐字符对比，0 差异才算通过
- **不要拿 markdown 导出对比**：ol 列表序号（"1."）是渲染产物，md 有而 XML 没有，会误报大量差异（本会话曾误报 263 处，实为 0）
- 场景/人物/台词骨架抽查：关键锚点文本按顺序存在、集数/章节序号连续

## 四、bot 身份创建文档 + 权限开通

**创建文档需要 `docx:document`（完整权限）**——create/readonly 子权限不够，会报 `missing_scopes: ['docx:document', 'docx:document:create']`。

**自动授权用户需要**：`docs:permission.member:create` + `drive:drive` + `drive:file` + `docs:doc` 等。缺这些时文档创建成功但 `permission_grant.status=failed`，用户打开看不到——**必须开通后才能让用户访问**。

**一次性申请链接**（把所需 scope 一次发给用户）：
```
https://open.feishu.cn/page/scope-apply?clientID=<appId>&scopes=<scope1>%2C<scope2>
```
（逗号 URL 编码为 %2C；自建应用通常免审核立即生效）

**验证成功**：创建返回 `permission_grant.status == "granted"`，`perm: full_access`。

**注意**：bot 创建文档时 `<title>` 标签不一定被识别为文档名（会显示 Untitled）——创建后用 `drive files patch --params '{"file_token":"...","type":"docx"}' --data '{"new_title":"..."}'` 修正（`--params` 必须带 `type`，否则报 missing required query parameter: type）。

## 五、富功能优化

- **Mermaid 时间轴**：`<whiteboard type="mermaid">` 直接插入 timeline 语法（主 Agent 可做，不需 SubAgent）。插入后 `whiteboard +export --output-type preview` 导出验证渲染——**preview 返回 .jpg，输出路径必须写 .jpg 扩展名**，写 .png 会报 failed_precondition
- **callout 高亮**：核心信息（一句话故事/核心冲突/画面锚点）用 `<callout emoji="🎬" background-color="light-purple" border-color="purple">` 提炼，插到章节开头
- 组件克制：大纲类文档加时间轴 + callout 即可；分栏/checkbox/@人按需，不堆砌

## 五·五、md 导入 docx 前的清洗（否则抬头脏）

**Obsidian/markdown 文件直接 `drive +import --type docx` 时，YAML frontmatter（`tags/date/updated/related`）会被当成正文显示在文档抬头**——用户会指出"抬头有不需要的东西"。导入前必须两步清洗：

```python
import re
content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.S)  # ① 删 YAML frontmatter
content = content.replace('\r\n', '\n')                          # ② CRLF → LF
```

验证：导入后 `docs +fetch --scope full` 检查内容开头无 `tags:`/`date:` 残留。

**改版替换策略**：内容改版后重新导入得到**新 token**，用 `drive +delete --file-token <旧token>` 删旧文档（保留新 token）——文件夹保持预期份数，不累积版本。

## 五·六、docs +update 文本替换（str_replace 模式）

`docs +update` 的 `str_replace` 命令用于文档内精确文本替换（如改一句台词/一个说法）：

- **匹配参数是 `--pattern`，不是 `--old-text`**（`--old-text` 会报 unknown flag）
- 替换内容用 `--content`，支持 `@file`（文件相对当前目录，**不接受绝对路径**——报 "must be a relative path within the current directory"；先 `cd` 到文件目录）
- 长文本（含换行）用文件承载：写 `newtext.txt` → `--content @newtext.txt`
- 替换后必须 **fetch 验证真的替换了**（str_replace 可能静默成功但 pattern 没匹配到）——`grep` 旧文本应为 0、新文本存在

**⚠️ 三大坑（2026-08-06 实测，都踩过）：**

1. **`--content ""`（空字符串）= 删除「所有」匹配，不是第一个**——文本中该片段出现 N 次就全删。曾因此把镜妖条目整段内容删光（片段出现 2 次，本想删重复却全删）。**删除重复/多余片段前先 `grep -c` 数清出现次数**；确认有重复时用 `block_replace --block-id` 替换整个 block 为正确内容，而不是 str_replace 删。
2. **XML 模式下 `--pattern` 只支持行内匹配，不能跨 block**——匹配目标若被解析为多个 block（如 `<h2>` 标题 + 段落内容），str_replace 会**静默失败**：返回 `ok: true` 但内容根本没变。**替换后必须 fetch 验证**，发现没变就改用 block 级操作。
3. **block 级内容（标题/整段/表格单元格）用 `block_replace --block-id`**：先 `docs +fetch --scope keyword --keyword <关键词> --detail with-ids` 拿目标 block ID，再 `block_replace --block-id <id> --content @file`。注意 `block_replace` 后旧 ID 失效——后续操作重新 fetch。

**行内 vs block 判断**：纯文本一句话（台词/短语）→ str_replace 行内即可；标题、整段、表格单元格、含样式嵌套的内容 → 直接走 block_replace，不要试 str_replace。

## 六、异步删除/移动容错

- `drive +delete` / `+move` 是异步操作：stdout 有 `Deleting.../Moving...` 前缀，操作可能已生效但 JSON 解析失败
- 重试报 `file has been delete` = 已删成功，不用再试
- 删除/移动是高风险写操作：先 `--dry-run` 预览，用户确认后加 `--yes`

## 七、移动后收尾

- `drive +move` 后 `drive files list --params '{"folder_token":"..."}'` 验证文件确实在新位置（返回 `name`/`type`/`token` 核对）
- 移动前可先 `drive +inspect --url` 确认目标文件夹类型与 token（folder 类型）
- bot 创建后标题可能显示 Untitled（见第四节）——移动/归档时顺便核对 `name` 字段，需要时用 `drive files patch` 补标题

## 相关

- [lark-doc](lark-doc/SKILL.md) — 文档读写命令语法
- [lark-drive](lark-drive/SKILL.md) — 云空间移动/删除/权限
- [lark-shared](lark-shared/SKILL.md) — 认证与 bot 权限处理
- `references/feishu-obsidian-sync.md` — 飞书↔Obsidian 文档关系（文档角色三分法：权威源/展示副本/独立定制版）——**不机械同步**（用户 2026-08-06 明确"别同步了"），项目上下文登记所有线（登记≠同步）
