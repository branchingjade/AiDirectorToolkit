# Web 工具后端：凭据 gate 诊断 + 后端选型与定价

> 2026-08-08 实测。背景：errors.log 出现 `check_web_api_key returned False`，web_search/web_extract 被 gate。本篇记录诊断链路、后端选项、定价快照。

## 1. check_web_api_key 判定逻辑（源码 tools/web_tools.py）

返回 False 的完整链路（OR 短路，全部不满足才 False）：

1. `config.yaml` 的 `web.backend`（或 search/extract_backend）非空 **且** `_is_backend_available()` 为真
2. 任一 `_LEGACY_WEB_BACKENDS` 可用：`{"parallel", "firecrawl", "tavily", "exa", "searxng", "brave-free", "ddgs", "xai"}`
   - exa/tavily/parallel → 对应环境变量存在（`EXA_API_KEY` / `TAVILY_API_KEY` / `PARALLEL_API_KEY`）
   - firecrawl → `FIRECRAWL_API_KEY`
   - **brave-free → `BRAVE_SEARCH_API_KEY`（不是 BRAVE_API_KEY！查错变量名会误判）**
   - searxng → `SEARXNG_URL`
   - **ddgs → `ddgs` Python 包可导入（唯一免 key 后端）**
3. 插件注册的 web provider 可用

## 2. 诊断命令（从外到内）

```bash
# 配置：web 段是否配了 backend
grep -A 5 "^web:" "$LOCALAPPDATA/hermes/config.yaml"

# 环境变量（注意 exact 变量名）
for k in EXA_API_KEY PARALLEL_API_KEY TAVILY_API_KEY FIRECRAWL_API_KEY BRAVE_SEARCH_API_KEY SEARXNG_URL; do
  [ -n "${!k}" ] && echo "$k = SET" || echo "$k = 空"
done

# 隐藏环境文件（LOCALAPPDATA/hermes/.env，真实密钥所在；~/.hermes/.env 只是壳）
grep -iE "API_KEY" "$LOCALAPPDATA/hermes/.env" | sed 's/=.*/=<redacted>/'

# ddgs 包是否存在（免 key 兜底）
"$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/python.exe" -c "import ddgs; print('OK')"
```

## 3. 后端选型与定价（2026-08-08 官方页面快照）

| 后端 | 计费模式 | 免费层 | 付费价 | 备注 |
|------|----------|--------|--------|------|
| **ddgs**（DuckDuckGo） | 免费 | 无限 | $0 | 免 key，pip install ddgs 即可；中文结果一般 |
| Tavily | 按量 pay-as-you-go | 1,000 credits/月（免绑卡） | **$0.008/credit**，4,000 credits/月起 | 搜索/抓取按请求类型扣 credits |
| Exa | 按量 | $10 额度 | 搜索 $7~15/千次；agent search tool call **$0.005/次**；复杂请求 $0.012~$1.00/次 | 专为 AI/agent 设计 |
| Firecrawl | 订阅制（无按量） | 1,000 credits/月（=1,000 页） | Hobby $16/月(5k页) → Standard $83/月(100k页) → Growth $333/月(500k页)，年付 | 1 credit = 1 页；反爬最强（能过 Cloudflare） |

定价会变——动手前用第 4 节方法重抓官方页确认。

## 4. 定价页抓取方法（JS 渲染页）

Exa/Tavily 的定价页是 JS 渲染壳，curl 直抓拿到的是空壳 HTML（wc -c 不小但正文是空的）。两条路：

```bash
# 首选：r.jina.ai 代取（Markdown 化，能拿到渲染后正文）
curl -sL --max-time 30 "https://r.jina.ai/https://exa.ai/pricing" -o exa.md
grep -iE '\$|credit|per search' exa.md

# 备选：直抓后本地提取（页面部分渲染时）
# 先 strip script/style → 去标签 → html.unescape → 按句号切句 → 过滤含 $/credits 的句子
```

提取要点：价格数字散在页面各处，`grep -oiE '\$[0-9]+(\.[0-9]+)?|credits' | sort | uniq -c` 看分布，再用句子级过滤（`re.split(r'(?<=[.!?])\s+')` + 含 `$` 且 <160 字符）拿上下文。

## 5. 实用结论（给用户选型时）

- 普通查资料/抓网页用量（几百次搜索/月）：免费层够用，ddgs 零成本先顶上
- 要付费时 Tavily 按量最划算（$0.008/次 ≈ 一千次搜索 $8，不订阅）
- 付费 API 相对 ddgs 的优势：结果质量高（带正文内容非纯链接）、反爬强（Firecrawl 能过 Cloudflare，如豆瓣/百度类墙）
- 浏览器工具（WebBridge/CDP）不受 web backend 影响，抓网页还有这条路
