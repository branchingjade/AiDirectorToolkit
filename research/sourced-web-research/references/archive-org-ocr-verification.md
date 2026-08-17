# archive.org OCR 全文的引文验证（2026-08-09 控方证人轮实测）

## 通道三步

1. **发现**：web_search `"<片名> screenplay"`（或 `"<书名> pdf"`）→ 命中的 archive.org 详情页。
2. **列文件**：`curl -sL "https://archive.org/metadata/<identifier>"` → JSON `files[]`。
   挑 `*_djvu.txt`（纯文本全文，OCR）或 `*_text.pdf`（可 pypdf 提取）；`*_hocr_searchtext.txt.gz` 也可用（压缩）。
3. **下载**：`curl -sL "https://archive.org/download/<identifier>/<文件名>"`，空格用 `%20`。

使用前先核版本声明：剧本首屏常印 "Final Script / <日期>"、编剧署名——引用时注明版本（一手来源的版本就是它的可信度标签）。

## 三级验证阶梯（对任何 OCR 存档）

1. **精确 grep**：原文大小写直接匹配。
2. **空白折叠**：`re.sub(r'\s+',' ', text).lower()` 后子串匹配——解决跨行劈词（OCR 每行截断，短语被换行切开）。
3. **OCR 归一化**：先做已知错字替换，再去标点，再匹配。

```python
def norm(s):
    s = s.replace('1s', 'is').replace('thet', 'that').replace('fell', 'fall')
    s = s.replace('prau', 'frau').replace('m faet', 'in fact').replace('fret', 'that')
    s = s.replace('wo ', 'we ').replace('eve @', 'what').replace('befọre', 'before')
    s = re.sub(r'[^a-z ]', ' ', s)   # 去标点必须放在替换之后！
    s = re.sub(r'\s+', ' ', s)
    return s.strip()
```

**顺序坑（实测踩过）**：先去标点再替换 = "1s" 先变 " s"，`replace('1s','is')` 永不命中。替换永远先于去标点。

## 已知错字映射表（控方证人轮实测，扫描 OCR 常见形态）

| OCR | 正确 | 形态 |
|---|---|---|
| 1s | is | 数字 1 代字母 i（最常见） |
| Prau / Mra / Nre | Frau / Mrs / Mr | 字母残缺 |
| thet / fret | that | |
| fell | fall | |
| m faet | in fact | 多字符错乱 |
| 4 | a | 数字代字母 |
| wo | we | |
| eve @ | What a | 严重损坏（不可恢复级） |
| befọre | before | 变音字符混入 |
| Tr | liar | 行尾截断（"chronic and habitual / Tr"） |

## 严重损坏行的处理纪律

OCR 烂到不可读（如 `eve @ remarkable woman!`、`chronic and habitual / Tr`）时：
- 用二手台词源交叉核对（**IMDb `/title/<id>/quotes/` 页经 r.jina.ai 代取成功**，2026-08-09 实测）；
- 交付物里**显式标注**"存档 OCR 为 X，按 [来源] 校正"——引文必须能解释来源，不许静默补全；
- 同词多处出现时优先引用完好那处（"remarkable woman" 中段句完好，结尾句损坏——引用中段并说明语境）。

## 工作样例

《控方证人》Final Script（archive.org id: `witness-for-the-prosecution-1957_202507`，10860 行）：
- 49 项引文验证：31 项剧本（精确+折叠+归一化）+ 18 项二手来源，最终全部 PASS；
- 2 处严重损坏行（L7652 "chronic and habitual/Tr"、L10795 "eve @ remarkable woman!"）按 IMDb 台词页/语义校正并在卡片中注明；
- 额外收获：剧本 L9846-9860 印 "THE FINAL 10 PAGES OF THIS SCRIPT WILL NOT BE ISSUED GENERALLY..."——一手实物证据，直接支撑"结局保密"论断，与维基二手叙述互证。
