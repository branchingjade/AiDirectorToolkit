# 科波拉深化轮 2026-08 — 校验脚本模式与 ref 剥除坑

科波拉手法体系深化轮（S1-S9 零存量全新建档，86 引文 0 MISS）实测产出的两个可复用资产：
①wiki raw 未闭合/嵌套 `<ref>` 导致的惰性正则跨段吞正文坑 + 嵌套感知剥除修复；
②引文校验脚本的片段提取/归属五条设计（配合 `scripts/verify_card_citations.py` 使用）。

## 一、坑：`<ref>` 惰性正则跨段吞正文（大面积假 MISS 的元凶）

**症状**：`re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)` 在 malformed wikitext 上把整段正文吞掉。
现代启示录英维 raw：245 个 `<ref` 仅 171 个 `</ref>`（未闭合/嵌套/自闭合混存）。惰性匹配把第一个坏
`<ref>` 配对到极远的 `</ref>`，中间正文全灭——目标引文（如 "the line just came to him"）根本不在
clean 文本里，引文校验报出一片假 MISS，连 "the line" 这种双词短语都查不到。

**排查顺序**：大面积 MISS 时**先怀疑剥除函数再怀疑引文**——对一个双词短语（任何英文文本必然出现的词）
做 `phrase in cleaned_text` 探针；False 即剥除函数吞文，不是引文抄错。

**修复：嵌套感知剥除**（先剥自闭合 `<ref .../>`，块 ref 按 `<ref`/`</ref>` 深度配对，无闭合剥到文末）：

```python
def strip_refs_robust(s):
    out, i = [], 0
    while True:
        j = s.find("<ref", i)
        if j == -1:
            out.append(s[i:])
            break
        out.append(s[i:j])
        m = re.match(r"<ref\b[^>]*/>", s[j:])   # 自闭合
        if m:
            i = j + m.end()
            continue
        k = j + len("<ref")
        depth = 0
        while True:
            nxt_o = s.find("<ref", k)
            nxt_c = s.find("</ref>", k)
            if nxt_c == -1:
                k = len(s)
                break
            if nxt_o != -1 and nxt_o < nxt_c:
                depth += 1
                k = nxt_o + 4
            else:
                if depth == 0:
                    k = nxt_c + 6
                    break
                depth -= 1
                k = nxt_c + 6
        i = k
    return "".join(out)
```

## 二、引文校验脚本五条设计（v2 实测有效）

1. **片段英文占比过滤**：只校验引号内「字母≥5 且 字母≥2×CJK」的片段。中文引号里的英文专名/预设名
   （如「暗光美学（Willis 低照度）」、「Prince of Darkness」讨论句）不是引文，不校验——否则合法假 MISS。
2. **归属=片段结束后的最近标签**（90 字符窗口内第一个 `[S#]/[卡X]/[研X]`），不用行内全部标签——
   表格单元格多标签时（科波拉轮：杜琪峰格引文 "No one shoots guns..." 行内还挂着 [卡教父]）会错挂存档。
3. **标签正则必须含 `研[^\]\s]+`**：本地资产前缀不止 卡/S（[研教父] 类），漏了会导致归属 fallback 到行首标签。
4. **诚实声明节整节跳过**：负面证据（「X 未取证到」）在存档里合法 MISS，跳过「## 5. 诚实声明」至「## 附录」。
5. **省略号/斜杠切段匹配**：片段按 `...`、`. . .`、`…`、`／`、`/` 切段，每段独立子串匹配——编辑性省略
   （如教父三结局原文中间还有 "Vincent shoots and kills Mosca."）=合法匹配单位；大小写回退单独计
   "case" tier 明示，不静默通过。

**文档侧配套纪律**：引文做中途省略时**必须在文档里写省略号**（`...`），否则校验按整段子串匹配必然假 MISS
（科波拉轮 4 处修正均属此类：漏 "(1979)"、漏 "Vincent shoots and kills Mosca."、逗号/句号变体、归属错挂）。

## 三、附属核对项

- **S# 双向对账的转引假越界**：正文含「[卡X 深化 §n 其 [S5]]」式转引时，朴素 `\[S(\d+)\]` 审计会把对方
  自建编号（如 [S32]/[S37]/[S38]）报为本文越界——正文显式声明「其 [S#] 为对方自建编号」即可，审计脚本
  加白名单或人工核对，不是文档错误。
- **并行轮共享存档同文判定**：两档字符数一致、前缀相同但 md5 不同时，写「对文（字符数一致，md5 微异）」，
  不写「同文」——md5 微异可能为修订差异（科波拉轮 cop_apoc_enwiki_raw.txt vs apocalypse_enwiki_raw.txt：
  均 144,376 字符，md5 不同）。
- **含引号内引号（nested quote）的引文**：norm 时先统一弯引号→直引号，再整体剥除引号字符再匹配——
  `a "total cipher" who lives alone` 与文档侧 `a 'total cipher' who lives alone` 因此等价。
- **「先怀疑脚本再怀疑文档」的判定案例**：教父卡片 "Do you renounce Satan?"（大写 D）初看是 case-tier，
  实为卡片另一行（画面锚点行）存在大写原句——exact 命中成立；查 exact 失败后先 grep -l 全部出现位置
  再判 tier。

## 四、科波拉轮产出

- 文档：`film-suite-research/技法卡片源稿/科波拉_手法体系深化.md`（241 行）
- 存档：pages/ 下 coppola_enwiki_raw（主条目，169KB）/ godfather2/3 / apocalypse / conversation /
  rainmaker / willis / heartsdark 共 9 档 enwiki raw（S1-S9）
- 校验：`film-suite-research/scripts/verify_coppola_deep.py`（86 条 exact 0 MISS 0 case）
- 关键结论：三线预设片序零证伪；「即兴与失控」四阶段链（压力临场→作者受控→生产即兴→重剪复权）；
  暗光美学=Willis 三部曲专用系统非终身；黑帮三系科波拉=神话一极（Ebert 封闭世界论+卫报李尔王论补直接文献）。
