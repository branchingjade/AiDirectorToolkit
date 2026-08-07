# juben.pro 剧本分页全文抓取（实测 2026-08-06 ·《新龙门客栈》13 页 / 175 场全量）

## 结论

华语剧本网 juben.pro 的剧本正文按页分片，**分页 URL 免登录/免 VIP 直接可读**。
旧认知（"免费只读前 N 场，全文需 VIP"）对分页作品不成立——先试分页 URL。

## URL 模式

```
作品页:    https://www.juben.pro/writing/<id>.html            （第 1 页）
分页:      https://www.juben.pro/writing/<id>-<n>-ccontent-hpdefault.html   （n = 2..N）
示例:      https://www.juben.pro/writing/4-15669-5-ccontent-hpdefault.html
```

- 页数从第 1 页底部「下一页 / 1 2 3 ... 13」链接里拿（evaluate 抓 `a[href*="ccontent"]`）。
- 第 1 页需要先点「阅读剧本正文」（文本含该字样的元素 `.click()`，DIV 即可；点击后 body len ~1.4K → ~4K）。
- **第 1 页重访坑**：同一 tab 再次 navigate 回第 1 页时，正文切片可能只取到 1 字符（页面状态/按钮态重置）——重导航+再点按钮，或直接从「编辑：」锚点前的正文段提取。

## 提取 JS（evaluate）

```js
(() => {
  const t = document.body.innerText;
  const j = t.search(/\d+、/);              // 第一个场次标题
  const k = t.indexOf('下一页');            // 分页尾
  const end = k > j ? k : j + 3200;         // 兜底
  return t.slice(j, end);
})()
```

写盘前 `replace('\x00','')`；「编辑：」之后是评论区/推荐样板，切掉。

## 合并 + 结构统计

```python
import re
# 场景标题：行首是全角空格 \u2003，必须 ^\s*
scenes = re.findall(r'^\s*(\d+)、([^，]+)，(日|夜|黄昏|黎明|清晨)(?:，|$)', text, re.M)
# 地点分布 → 统计"单一空间戏份占比"（如新龙门客栈：客栈内外 116/153 ≈ 76%）
```

## 版本与质量注意

- 网版流传稿，与上映版有出入：人名用字（贾延/贾廷、路小川/陆小川）、台词措辞、录入瑕疵（"一百量/鬼门光"）。引用注明"网版流传稿 + URL + 场次号"。
- 剧本正文若 evaluate 返回空但页面有内容 → display:none 容器，改 `textContent`（见主 SKILL.md）。
- 缺页补齐：知乎专栏搜「电影剧本《片名》」常有同文片段（如 zhuanlan.zhihu.com/p/421095121 含《新龙门客栈》1-10 场，结尾"关注 GZH 获取完整剧本"）。
- 素材落盘后 read_file 可能误报 binary（CRLF+中文、无 NUL）→ 用 Python `open().read()`。

## 实测档案（新龙门客栈）

- 作品 id `4-15669`，13 页，场景 1–175，合并稿 31,774 字符存 `film-suite-research/_source/longmen_script_juben_full.md`
- 三幕推断：44 场客栈剪彩（25.1%）、73 场东厂入驻四方聚齐（41.7%）、113 场洞房混战（64.6%）、172 场流沙决战（98.3%）
- 编剧网版署名：徐克 / 张炭 / 吕晓禾 / 司徒慧焯 / 何冀平 / 苏叔阳
