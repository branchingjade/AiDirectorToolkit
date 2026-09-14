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

## 四·五、文档权限诊断三步法（"有管理权限但改不了"排查）

用户报「挂了管理权限为什么文档改不了」时，**先诊断再动手，不要信口头权限描述，更不要默认是权限问题**（2026-08-13 实测：根因是评论 agent 工具集没挂写工具，权限完全够）。三步：

1. **查协作者列表**：`lark-cli drive +member-list --token <token> --type docx --as bot --fields "*"`（bot 身份可查，不需额外 scope；user 身份反而要 `docs:permission.member:retrieve`）。列表里没有 bot 应用 **≠ 没权限**——文档还有公开权限层。
2. **查公开权限设置**：`lark-cli drive +permission-get-setting --token <token> --type docx --as bot`。关键字段 `link_share_entity`：**`tenant_editable` = 租户内所有应用/用户可编辑**（bot 属租户 → 能写）；`closed` = 只限协作者列表。
3. **写探针（无副作用）**：`docs +update --command str_replace --pattern "<文档中不可能存在的串>" --content "x"`。返回 `ok:true` + `result:failed`（degrade_code=1011 no document changes）= **权限通**（只是没匹配到）；返回 permission denied = 真没权限。

**可逆全链路验证**：pattern 用真实存在的词、content 加独特标记（如「妖丹→妖丹♯」），执行后 fetch 验证计数，再改回，确认零残留。这在真实文档上安全，不动正本内容。

**文件夹权限 ≠ 文档权限**：文件夹 member-list 有管理权限不代表内部文档能改——文档权限 per-file 且可能不在该文件夹/已单独设权。别被「共享文件夹管理权限」误导，直接查目标文档本身。

## 四·六、docx 写操作端点速查（docs_ai，lark-cli docs +update 底层）

写工具/脚本直接用这两个 OpenAPI 端点（lark-cli `docs +update`、评论 agent 的 feishu_doc_* 工具都走这里）：

- **读 with-ids**：`POST /open-apis/docs_ai/v1/documents/:id/fetch`，body `{"export_option":{"export_block_id":true},"format":"xml"}` → 返回带 `<p id="...">`/`<h1 id="...">` 的 XML（定位 block_id 用）
- **写**：`PUT /open-apis/docs_ai/v1/documents/:id`，body `{"command":"str_replace|block_replace","pattern":...,"content":...,"format":"xml","revision_id":-1}`；`block_replace` 额外带 `block_id`，content 是完整 XML 块（`<p>...</p>`/`<h1>...</h1>`）
- str_replace 返回 `result:failed` + degrade_code=1011 = pattern 没匹配或替换后相同，**不代表失败**——判断成功看 revision 变化 + fetch 验证
- **block_replace 后旧 block_id 失效**（实测 id 会变，如 `McCCdluIgo...` → `doxcnVkPcsqRsd59bbRBks0Zhuh`），继续操作必须重新 fetch
- 认证走 `AccessTokenType.TENANT`（bot 身份）；lark_oapi Client 构造 `log_level` 必须传枚举 `LogLevel.WARNING`，传 int 报 `'int' object has no attribute 'value'`
- 工具发现缓存（tool_discovery_cache.json）按 `(mtime_ns, size)` 自动失效——改 tools/*.py 后无需手动清缓存

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

## 五·七、docs 嵌入图片到 docx（图文并茂类创作产出的坑矩阵，2026-09-03 伏妖记美术考据实战）

飞书 docx 文档要"图文并茂"——必须用 `docs +media-insert` 嵌入本地图片，**不是** markdown `![alt](URL)`。下表是踩过的实战坑矩阵，按"症状→根因→修法"组织。

### 坑 1：markdown 图片语法 `![](URL)` 不触发飞书下载

**症状**：`docs +update --content @file.md` 时文件含 `![越王勾践剑](https://upload.wikimedia.org/.../越王勾践剑.jpg)` → API 返回 `ok:true` + `revision_id` 推进 + **`result:partial_success` + `warnings: ["degrade_code=2108,msg=Image download failed. image URL: ..."]`**——文字部分写进去了，**图占位符留下但没图**。

**根因**：飞书 docx 写操作是「文字+图占位符」分两步：①把 markdown 解析成 DocxXML，文字正常落盘；②对每个 `![](URL)` 的 URL 异步取图（HTTP 下载），失败就 degrade。Wikimedia Commons 的 URL（含 UTF-8 中文文件名 + utm 参数）经常被飞书服务端 fetch 失败（地区限制 / User-Agent 拒 / 编码问题）。

**修法**：**不要指望 markdown 图片语法落图**——必须先把图下载到本地，再 `docs +media-insert`。

### 坑 2：Wikimedia Commons 是「真」图源，但中文文件名要 urllib.parse.quote

**症状**：在浏览器看到的 Wikimedia URL 是 `https://commons.wikimedia.org/wiki/File:越王勾践剑.jpg`，但 `requests.get(url)` 404——因为浏览器跳转后的真实文件 URL 是 `https://upload.wikimedia.org/wikipedia/commons/b/bd/<urlencoded>`。

**修法**：用 Wikimedia 自己的 `Special:FilePath/` 中转——它会把 `File:<filename>` 302 跳到实际文件 URL。**HEAD 探测 + urllib 拉**：

```python
import urllib.request, urllib.parse
url = f'https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote("越王勾践剑.jpg")}'
req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as r:
    real_url = r.url  # 真实文件 URL
# 再 GET 拉真实 URL
req = urllib.request.Request(real_url.split('?')[0], headers={'User-Agent': 'Mozilla/5.0'})
data = urllib.request.urlopen(req, timeout=30).read()
```

**限流**：429 Too Many Requests 是 Wikimedia 高频抓取的常态——加 `time.sleep(5-8)` 退避重试，不要高频 hit。

**压缩大图**：Wikimedia 原图常常 5-10MB（清明上河图原图 10MB）。飞书 `docs +media-insert` 支持 20MB 以下自动分块，但大图会让 doc 翻页卡顿。**预先 ffmpeg 压缩**：

```python
ffmpeg -y -i 清明上河图.jpg -vf 'scale=2400:-2' -q:v 5 清明上河图_small.jpg
# 10MB → 490KB，宽度 2400px
```

### 坑 3：lark-cli 的 `--file` 必须是 cwd 相对路径

**症状**：`docs +media-insert --file C:/Users/HMSJ/_content/imgs/foo.jpg` 报 `unsafe file path: --file must be a relative path within the current directory, got "C:\\..."`。**绝对路径一律拒**。

**修法**：把图片复制/软链到 cwd 下再调——cwd 通常是 `C:/Users/HMSJ/Documents/Hermes/`：

```python
import shutil, os
src = r'C:\Users\HMSJ\_content\imgs'
dst = r'C:\Users\HMSJ\Documents\Hermes\_imgs'
if os.path.exists(dst): shutil.rmtree(dst)
shutil.copytree(src, dst)
# 然后 --file ./_imgs/foo.jpg
```

**同样的 cwd-相对约束也适用** `docs +update --content @file.md`（坑 4 是这条的下游）。

### 坑 4：`docs +update --command overwrite` 会把已有图片冲掉

**症状**：`docs +update --command overwrite --content @file.md` 看起来是「文本完全替换」——实际上**会把所有已有图片块（image block）当成内容被覆盖**，冲掉的图片落到文末（`media-insert` 之后的图反而被 `overwrite` 之后的内容推到末尾）。

**修法**：**顺序固定**——

1. 先把文本（不含 markdown 图片语法）通过 `docs +update --command overwrite` 写进去
2. **最后一次** `overwrite` 之后，再 `docs +media-insert` 逐张插图
3. 如果之后还要改文本——用 `str_replace`/`block_replace`，**不要再次 overwrite**（再次 overwrite 会把刚插的图也冲掉）

**验证图存在**：`docs +fetch --scope full --detail full --format pretty` 后 `grep -E '<img [^>]*name="[^"]+"'` 看 doc 里实际嵌入的图片文件名清单。

### 完整的「图文并茂」工作流

1. **列文物/考据图源**（实物名 + 藏地 + URL）清单
2. **Wikimedia 探测**：用 `Special:FilePath/<文件名>` HEAD 探测可达性，命中即 urllib 拉到 cwd 下 `_imgs/<name>.jpg`
3. **大图压缩**：>3MB 的图用 ffmpeg 缩到 2400px + q:v=5（实测清明上河图 10MB→490KB）
4. **写文本**：`docs +update --command overwrite --content @<text>.md`，文本**不要含** markdown 图片语法
5. **插图**：`docs +media-insert --file ./_imgs/<name>.jpg --doc <token> --caption "<图注>" --width 1200`，每张图一次调用
6. **验证**：fetch + grep `name=` 确认全部图嵌入

### 命令模板（可复制）

```python
# 1) Wikimedia 探测 + 下载
import urllib.request, urllib.parse, time
url = f'https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote("<FILE>")}'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    real_url = urllib.request.urlopen(req, timeout=10).url.split('?')[0]
    time.sleep(2)  # 防 429
    data = urllib.request.urlopen(real_url, timeout=30).read()
    open(r'C:\Users\HMSJ\Documents\Hermes\_imgs\<NAME>.jpg', 'wb').write(data)
except Exception as e:
    print(f'FAIL: {e}')

# 2) ffmpeg 压缩（仅大图）
import subprocess, os
src = r'C:\Users\HMSJ\Documents\Hermes\_imgs\<NAME>.jpg'
dst = src.replace('.jpg', '_small.jpg')
ffmpeg = r'C:/Users/HMSJ/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.1-full_build/bin/ffmpeg.exe'
subprocess.run([ffmpeg, '-y', '-i', src, '-vf', 'scale=2400:-2', '-q:v', '5', dst])

# 3) 写文本（注意：不含 markdown 图片语法）
# docs +update --doc <token> --doc-format markdown --command overwrite --content @<text>.md

# 4) 插图
# docs +media-insert --doc <token> --file ./_imgs/<NAME>.jpg --caption "<CAPTION>" --width 1200
```

### 坑 5：Wikimedia 文件名可能误导——下载后必须 vision 验证「图对得上名」

**症状**：用 Wikimedia Commons Special:FilePath HEAD 探测 200、文件大小正常、视觉看起来是「考据要的器物」——但实际是**自然/无关的物体**。典型踩坑：`Garuda_cliff_in_Tirumala` 文件名带 Garuda 但下载下来是印度 Tirumala 天然山崖（不是金翅鸟雕像/壁画）；commons 没真正的李思训《江帆楼阁图》台北故宫真迹——能下到的是后摹本/仿本，但图片本身范式是金碧山水。

**根因**：
- Wikimedia 命名不规范，同名近义不同物（cliff / statue / painting 都是不同分类）
- Commons 没有的真品（国宝/限藏）会被仿本/后摹本/错误归类填位
- 中文维基/commons 的命名有时采用英文维基翻译后的文件名，跟原典不一致

**修法**：
1. 下载后**用 vision 工具（vision_analyze / GPT-4V / 多模态）验证图内容**——问「这是 X 吗？」答 yes 才用
2. 在飞书 caption 里**老实标注来源类型**：「WikiCommons 来源仿/摹本」「WikiCommons 命名为 X 但实为 Y（参考用）」——失败也保留作为范式类
4. 错图用 `docs +update --command block_delete --block-id <id>` 删除；**不要用 block_replace 替换为 caption 文本**（见坑 6）

**诊断口诀**：图嵌入飞书后第一件事——打开飞书 doc 用 vision 验证所有图对得上考据名/文物名/角色名。任何"文件名对但内容不对"的图立刻删+留档补图需求。

### 坑 6：`docs +update --command block_replace` 不能用来改 image block 的 caption

**症状**：对已嵌入的图（image block），用 `docs +update --command block_replace --block-id <img_block_id> --content "新 caption"` 想只改 caption——结果**整张图被替换为 caption 文本块**，图块消失。

**根因**：`block_replace` 是「用一个 block 替换另一个 block」——`--content` 是新 block 的完整 XML（`<p>...</p>` 之类）。传 caption字符串 = 创建一个新 paragraph block 替换 image block = 图没了。

**修法**：
- **改 caption 用 `block_replace --content "<img ... caption=\"新cap\">"`**——传完整 `<img>` 标签（带新 caption），不是纯文本
- 或者更稳妥：**删旧图 + media-insert 新图**：
  ```
  docs +update --command block_delete --block-id <old_img_id>
  docs +media-insert --doc <token> --file ./_imgs/foo.jpg --caption "新 caption"
  ```
- **不要碰 image block_id 的 str_replace**——str_replace 只能改行内文本，image block 整块编辑路径都不可靠

### 何时加载本节

- 用户说「图文并茂」「附图」「放文物图」「贴参考图」到飞书 docs
- 用户要求做"美术/服装/场景/道具"考据+图片证据链
- 接到任何"写飞书文档+要图"的任务（剧本插图、分镜示意图、产品展示文档）
- 飞书 docs +update 报 `partial_success` + `degrade_code=2108`——立刻跳到这里
- 已嵌入图的 caption 需要改——用「传完整 <img> 标签」或「删旧插新」，别用 caption 纯文本替换

### 配套脚本

完整工作流脚本见 `references/feishu-doc-image-embed-workflow.md`——包含 Wikimedia 探测 + urllib 下载 + ffmpeg 压缩 + media-insert 顺序的全套落地代码 + 错误处理 + 429 退避。

---

## 六、异步删除/移动容错

- `drive +delete` / `+move` 是异步操作：stdout 有 `Deleting.../Moving...` 前缀，操作可能已生效但 JSON 解析失败
- 重试报 `file has been delete` = 已删成功，不用再试
- 删除/移动是高风险写操作：先 `--dry-run` 预览，用户确认后加 `--yes`

## 七、移动后收尾

- `drive +move` 后 `drive files list --params '{"folder_token":"..."}'` 验证文件确实在新位置（返回 `name`/`type`/`token` 核对）
- 移动前可先 `drive +inspect --url` 确认目标文件夹类型与 token（folder 类型）
- bot 创建后标题可能显示 Untitled（见第四节）——移动/归档时顺便核对 `name` 字段，需要时用 `drive files patch` 补标题

## 八、bot 私发文档到指定用户 DM（Doc + IM 全链路）

bot 身份创建 Doc + 给目标用户开 view + 在其 DM 发链接，组成「bot 私发文档给指定用户」闭环——区别于第四节「bot 身份创建 + 权限开通」（只到文档创建就停）。

**典型触发**：「把这个发给我」「把这个发到 XX 会话」「给 YY 发文档」「把 XX 通过飞书发给 YY」。**bot 身份合规**——满足「Hermes bot 身份发对外消息」铁律。

完整配方（含 `+get-user` 在职核查、`+member-add --type docx`、三步验证、踩坑清单、实战案例）见 [`references/bot-dm-delivery.md`](references/bot-dm-delivery.md)。

辅助脚本 `scripts/docx_to_feishu_markdown.py`：docx → markdown，**保留段落+表格交错顺序**（按 `body.iterchildren()` 遍历，绕过 `d.paragraphs` 不含表格的坑）。用于源文件是 docx 而非现成 .md 的场景。

## 相关

- [lark-doc](lark-doc/SKILL.md) — 文档读写命令语法
- [lark-drive](lark-drive/SKILL.md) — 云空间移动/删除/权限
- [lark-shared](lark-shared/SKILL.md) — 认证与 bot 权限处理
- `references/feishu-obsidian-sync.md` — 飞书↔Obsidian 文档关系（文档角色三分法：权威源/展示副本/独立定制版）——**不机械同步**（用户 2026-08-06 明确"别同步了"），项目上下文登记所有线（登记≠同步）
- `references/feishu-doc-image-embed-workflow.md` — 飞书 docs「图文并茂」图源工作流：Wikimedia 探测 + urllib 下载 + ffmpeg 压缩 + media-insert 全套落地代码 + 错误处理 + 429 退避。Use when 创作类产出要"图文并茂"（剧本插图/美术考据/分镜示意图）
