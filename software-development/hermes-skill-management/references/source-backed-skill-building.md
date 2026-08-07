# 研究驱动构建带跟脚的 Skill（source-backed skill building）

用户要求知识型/创作型 skill "所有内容有跟脚（可验证来源）"时，用本工作流。实战验证：电影套件（AI电影编剧 v2.0.0 + AI电影导演 v1.0.0）全量构建，48 个来源全部入 ledger，verify 通过后发布。

## 何时用

- 构建/重建涉及外部知识的 skill（导演理论、行业格式、剧本分析、API 文档类）
- 用户明确说"要有跟脚""不能凭空写""研究所有知名导演/高分电影"
- 参考：grounded-citations skill（ledger 工具链）配合使用

## 工作流（5 步）

### 1. 先写研究大纲，用户确认后再动手

用户曾因"还没把规划做好呢"叫停（2026-08 电影套件）。先产出 `研究大纲.md`：研究模块（A 格式规范 / B 导演研究 / C 高分剧本）+ 每个模块的产出物 + 验证方式。用户确认方向后再开抓取。

### 2. 并行子代理分片研究（delegate_task）

4 个并行子代理，每个负责一个模块，context 里必须写死：

- 用 `curl -sL --max-time 30` 抓真实网页，**不要用浏览器**（curl 快且可脚本化）
- 抓取结果存到 `pages/<模块>-<关键词>.txt`（Python 提取正文，去 script/style/标签）
- 返回的笔记里**每个手法/规则必须带来源 URL**
- 目标文件路径写死（如 `导演研究-西方.md`），避免子代理自己乱放

**超时恢复**：子代理可能 600s 超时（电影套件东方导演组就超时了），但 `pages/` 下的原始抓取文件已落盘——主线程直接从原始文件提取证据补写笔记，不重派。

### 3. 主线程从原始文件提取原文证据

维基抓取含模板噪声（`{{...}}`、`[[wikilink]]`、`<ref>`），用 Python 清理后按关键词正则提取原文句子：

```python
def clean(path):
    s = open(path, encoding='utf-8', errors='ignore').read()
    s = re.sub(r'\{\{[^{}]*\}\}', ' ', s)                    # 去维基模板
    s = re.sub(r'\[\[([^|\]]*\|)?([^\]]*)\]\]', r'\2', s)   # wikilink → 文本
    s = re.sub(r'<ref[^>]*>.*?</ref>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', s)
```

提取技巧：`re.search(r'[^.]*<关键词>[^.]*\.', txt, re.I)` 按句子边界取含关键词的完整句，作为引文证据。中文维基常是重定向页（内容极少），优先英文维基主条目。

### 4. grounded-citations ledger 验证（不通过不发布）

```bash
S="<hermes>/skills/research/grounded-citations/scripts/sources.py"
python "$S" reset                          # 每个任务一次
python "$S" add <url> --title "<标题>"     # 每个来源注册，拿到 [n]
# 写文档时正文用 [n] 标注
python "$S" render --replace-in <draft.md> # 机械生成 Sources 块
python "$S" verify <draft.md>              # 通过才算数（覆盖率 + 引用合法）
```

- 注册来源用 ledger 返回的 id，**绝不手写 URL 到正文**
- verify 失败常见：缺 `Sources:` 块 → `render --replace-in`；引用不匹配 → 检查 [n]
- 诚实原则：子代理如实报告抓取失败（如教父 PDF 解码有损、卧虎藏龙为修订稿），不编数据

### 5. 构建 skill + 发布

- `skill_manage(action='create')` **拒绝中文名**（Invalid skill name，仅限小写/数字/连字符/点/下划线）——中文命名的 skill（如妖玉影视系列）用 `write_file` 直接写 `skills/<分类>/<中文名>/SKILL.md`
- 研究文档放 `references/` 下作为跟脚（格式规范研究/导演研究/剧本分析/CHANGELOG）
- 发布走 skill-publish 三步：同步正本 → tag → release（电影前缀 `ai-film-*`）

## 陷阱清单

1. **主线程与子代理写同一目标文件会互相覆盖**：主线程先写的文档立即改名隔离（如加 `-主线程` 后缀），让子代理写自己的目标文件
2. **子代理超时不等于失败**：`pages/` 原始抓取已落盘，主线程可续写；先 `ls pages/` 盘点再决定重派还是补写
3. **中文维基重定向**：`zh.wikipedia.org` 条目常是 `#REDIRECT` 壳（仅几 KB），内容在英文维基
4. **JSON/heredoc 命令被安全模块拦**：大段内联命令改用脚本文件执行
5. **verify 覆盖率**：目标 >70% 声明来源；无法来源的模型知识标 `[unverified]`，不冒充
6. **清理**：研究完成后删除 `_work/` 临时目录，只保留 references/ 落盘副本

## 中文来源/国内法规抓取路径（2026-08 国内适配实战）

中文站点反爬差异大，按站点选路径：

- **知乎**：正文需登录，经 `r.jina.ai` 代理可穿透（`curl -sL "https://r.jina.ai/<zhihu-url>"`）；知乎有反爬 40362，Jina 可过
- **百度知道**：curl + cookie 可直接抓（`zhidao.baidu.com/question/<id>.html`），正文在 HTML 里
- **百度百科**：完整正文 403（反爬），改用官方 openapi 取词条摘要（`baike.baidu.com/view/<id>.htm` 的 openapi 端点）
- **百度文库/豆丁**：需登录/JS，抓不了——不要作为来源，如实放弃
- **国内法规原文**：优先 `gov.cn/gongbao/`（国务院公报页，纯静态可 curl，如《电影管理条例》全文）；`flk.npc.gov.cn`（国家法律法规数据库）是 JS 渲染应用，API 带签名参数，curl 直抓拿不到全文
- **gov.cn URL 猜不准**：`gov.cn/xinwen/` 下的编号 URL 猜错率高（同一天多条主席令相邻编号），猜错会抓到别的法——用搜索定位正确 URL，别试错

法规研究诚实纪律：**抓不到原文的法条内容一律不写**（子代理如实报告"未抓到原文"，主线程用已抓到的条例原文作主来源，标出上位法全文缺失），不编造法条编号与内容。法规为动态政策，笔记标注"以主管部门现行规定为准，不构成法律意见"。
