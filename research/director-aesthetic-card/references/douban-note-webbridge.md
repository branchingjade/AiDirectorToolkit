# 豆瓣笔记（note）经 Kimi WebBridge 抓取配方（2026-08-07 无人知晓轮实测）

## 场景

- 豆瓣 **notes**（`www.douban.com/note/<id>/`）对 curl 与 r.jina.ai 都是 JS 壳：curl 拿"载入中..."，jina 只回 119 字节（`Title: 豆瓣` / `载入中 ...`）。
- notes 是中文**剧本拉片转写 / 访谈转帖 / 长文**的主战场——无官方剧本的片子先搜 note：《无人知晓》206 场全片拉片转写稿（对白+镜头描述）即 `note/732001658`（标题《无人知晓》剧本 By 是枝裕和（个人拉片，禁止转载））。
- 发现路径：r.jina.ai 代理 DDG HTML（`https://r.jina.ai/https://html.duckduckgo.com/html/?q=<url编码>《片名》 剧本 导演`）→ 结果里的 `douban.com/note/` 链接即候选。

## 配方（全部实测有效）

1. **探活**：`curl -s -m 15 http://localhost:10086/status` → 看 `extension_connected:true`，false 则 navigate 必失败。
2. **唯一 API 入口**：`POST http://127.0.0.1:10086/command`，body 顶层三字段：
   ```json
   {"action":"navigate","args":{"url":"https://www.douban.com/note/732001658/","newTab":true,"group_title":"无人知晓研习"},"session":"nobody-3f7a9c2e"}
   ```
   - 裸 `/navigate`、`/evaluate` 路径 **404**；浏览器 CDP `Runtime.evaluate` **不可用**——只有 /command 是活的。
   - `session` 命名 `<任务>-<8位hex>`，同一任务全程不变（tab 分组）。
   - 返回 `{"ok":true,"data":{"success":true,"url":...,"tabId":...}}`。
3. **读文本**：`{"action":"snapshot","args":{}}` → 返回 JSON 树（大页面可达 300KB+，curl 落盘再解析）。
   - ⚠️ `{"action":"evaluate","args":{"code":"document.body.innerText"}}` 实测返回**空串**（页面渲染未就绪或壳结构）——**snapshot 树提取才是可靠路径**。
4. **Python 递归 walk 树取全文**（节点结构为 dict 或 list 嵌套）：
   ```python
   lines = []
   def walk(node):
       if isinstance(node, dict):
           if node.get('role') == 'StaticText' and node.get('name'):
               lines.append(node['name'])
           for c in node.get('children', []) or []:
               walk(c)
       elif isinstance(node, list):
           for c in node:
               walk(c)
   walk(tree)
   text = '\n'.join(lines)
   ```
5. **清洗**：全文含豆瓣 UI 头（登录/注册/导航/话题广场）与尾部（版权块/热门话题/©2005-2026 douban.com）。用正文首个场景标记切头（如 `1.电车`），用 `本文版权归` 切尾。
6. **Windows 坑**：含中文的 JSON body 必须用 write_file 写唯一命名的 JSON 文件，再 `curl -X POST ... --data-binary "@file.json"`——shell 内联 JSON 会损坏非 ASCII（幂等性：每个请求单独一个文件）。
7. **引用标注**：note 多带"禁止转载"声明（原文"任何形式转载请联系作者"）——存档与引用须注明"个人拉片/转写，非官方剧本，禁止转载声明来自原作者"；与成片可能有少量出入（如数量细节），研习报告诚实声明里列明。

## 无人知晓轮结果

- `note/732001658`：206 场全片拉片转写（含对白+镜头描述）→ 存档 `pages/nobody_douban_note_script.txt`，入库 `剧本原文/nobody_剧本_来源.md`（YAML frontmatter 标注转写性质）。
- 途中失败留档：`/navigate`、`/evaluate` 裸路径 404；CDP `Runtime.evaluate` 报 `-32601 not found`；jina 抓 note 只回 119 字节壳。
