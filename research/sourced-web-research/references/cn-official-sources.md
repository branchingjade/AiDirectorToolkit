# 中国大陆官方源抓取速查（2026-08 实测）

来源：研究《电影产业促进法》/电影备案审查制度时的实测记录。标注 ✅=已实测验证，⚠️=候选/未核验，❌=实测不可行。

## flk.npc.gov.cn 国家法律法规数据库（Vue SPA + 反爬，难啃）

- ❌ curl 只能拿到 SPA 壳（`index.html` + `/assets/index-*.js`）；旧教程的 `POST /api/search` 已失效（405 Not Allowed）。
- ❌ 现行 API 直连也被拒：`POST /law-search/search/list` 返回 `{"msg":"系统异常","code":500}`（反爬，需浏览器会话与正确 payload——payload 结构在 SPA 分包里，未逆向出）。
- ✅ 现行 API 端点清单（从 `https://flk.npc.gov.cn/assets/index-Y9B5oxpu.js` 提取）：
  `law-search/search/list`（POST 检索）、`law-search/search/flfgDetails`（法规全文）、`law-search/search/hitDisplay`、`law-search/search/xgzl`、`law-search/highSearch/highSearch`、`law-search/download/pc`、`law-search/download/batch`、`law-search/amazonFile/previewLink`。
- ✅ 浏览器可用深链直接出结果：`https://flk.npc.gov.cn/search?searchType=title;accurate&searchValue=<URL编码关键词>`（实测渲染出结果列表与检索条件）。
- ✅ 结果条目 DOM：`div.result-item`，元数据含：时效（有效/已修改）、公布日期、施行日期、类别（法律/行政法规/地方法规/司法解释）、制定机关。实测《电影产业促进法》：有效、2016-11-07 公布、2017-03-01 施行、法律、全国人大常委会。
- ⚠️ 打开全文：点击 result-item 行（JS `.click()` 不触发 Vue 导航，会另开 `/search` 标签页）。**截至 2026-08 全文抓取路径未跑通**——不要把预算耗在这，直接换镜像源。

## gov.cn 中国政府网

- ✅ 所有 `http://www.gov.cn/*` 永久 301 → https：curl 必须 `-L`。
- ✅ 链接腐烂严重：旧 xinwen 全文页（如 2016-11-07《电影产业促进法》全文 `content_5129757.htm`）已 404——老链接先验状态码再引用。
- ✅ 国务院公报全文页仍存活：`https://www.gov.cn/gongbao/content/<年>/content_<id>.htm`（实测 200）。⚠️ **id 不能凭记忆猜**：`content_61858.htm` 实际是"国务院办公厅关于成立第29届奥组委领导小组的通知"而非《电影管理条例》；`content_61864.htm`（经 DDG 检索命中，疑似《电影管理条例》）正文未核验。
- ❌ 站内搜索 sousuo.www.gov.cn：curl 与浏览器渲染均返回"抱歉，没有找到相关结果"（0 条，含/不含 dataTypeId=107 都试过）——对自动化不可用，改用外部引擎或直爬栏目页。

## 搜索引擎（curl 实测）

- ✅ **DDG html 版**：`curl -s -A "$UA" "https://html.duckduckgo.com/html/?q=<url编码>"`；真实 URL 在 `uddg=` 参数里（url-decode 即最终地址）。成功定位 gov.cn 公报页与 xzfg.moj.gov.cn 条目。⚠️ 限流极快：连发 2+ 查询即 202，页面含 "anomaly" 字样；查询间 sleep 8–15s。
- ❌ Bing：`format=rss` 返回空；HTML 结果链接包成 `bing.com/ck/a?...&u=a1...` 重定向；且查询串含 `site:gov.cn` 时朴素 `grep -oE 'https?://[^"&]*gov\.cn'` 会匹配到搜索 URL 本身（误报）。
- ❌ 百度/搜狗：302 反爬，curl 拿不到正文。

## chinafilm.gov.cn 国家电影局（服务端渲染 TRS，curl 友好 ✅）

- 首页 200，HTML 可解析；频道链接模式 `/chinafilm/channels/<id>.shtml`（首页出现 138/146/147/150/175）。
- 「政策法规」栏目相对路径 `./xxgk/zcfg/`（即 `https://www.chinafilm.gov.cn/chinafilm/xxgk/zcfg/`）。
- 电影备案/审查制度（剧本梗概备案、电影片审查、公映许可）的权威发文渠道。

## xzfg.moj.gov.cn 司法部行政法规库（⚠️ 候选源）

- 行政法规详情 URL 模式：`https://xzfg.moj.gov.cn/law/detail?LawID=<id>`（如 LawID=584 经 DDG 命中《电影管理条例》，正文未核验）。
- 行政法规（国务院令）优先查这里或 gov.cn 公报。

## 浏览器工具对中文政府页的编码坑（✅ 已验证解法）

- `browser_navigate` 对部分中文政府页（GBK/混合编码）抛 `'utf-8' codec can't decode byte 0xb2 ...`。
- 解法：先 `browser_cdp Target.getTargets` 拿现有 tab 的 targetId，再 `browser_cdp Page.navigate {url, target_id}`，随后 `browser_cdp Runtime.evaluate {expression: 'document.body.innerText', target_id}` 读正文（在 flk.npc.gov.cn 与 sousuo.www.gov.cn 上验证有效）。

## 反爬现实与预算纪律

- 官方库（flk）SPA+反爬最难啃；**先花 10 分钟试平行权威镜像**（国务院公报、部门官网、司法部行政法规库），别把预算耗在单一 SPA 逆向上。
- 法规/条文原文抓不到完整版时：如实标注"未抓取/未核验"，绝不凭记忆补法条。
