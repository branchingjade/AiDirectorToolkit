# 火山引擎豆包语音 用量/配额监控 API 调试笔记（2026-08-11 实测）

场景：doubao-tts-server 的 `/quota` 余额显示。核心目标：拿到账号真实 ResourceID → 查资源包剩余/调用量。

## 一、三个监控 OpenAPI（open.volcengineapi.com，SignerV4 签名）

Service=`speech_saas_prod`、Region=cn-north-1、Host=open.volcengineapi.com。鉴权 = 火山 OpenAPI 签名（AK/SK），**不是** openspeech 的 X-Api-Key。volcengine SDK（1.0.x，非 1.9x）+ SignParam/SignerV4。

| 接口 | Version | 必选参数 | 实测行为 |
|---|---|---|---|
| `ResourcePacksStatus`（资源包剩余） | 2025-05-20 | **ProjectName 必选**（缺了报 500 InternalError！）+ ResourceIDs[] + **Types 必传**（`["access","quota","prepaid"]`，**不带返回 TotalCount=0 空数据**！）+ 可选 PageSize/PageNumber | 返回 `Packs[].Harvest{PurchasedAmount,CurrentUsage,Unit}` + `TotalHarvests[]`；剩余=购买-已用，Unit 实测为中文（如「分钟」）；`Packs[].InstanceNumber`=资源包实例号（如 SeedAudio1.0...）、`Packs[].Code`=资源包代码 |
| `QuotaMonitoring`（配额查询） | 2025-05-21 | ProjectName + ResourceID + Start/End（yyyy-MM-dd）+ Mode=daily + QuotaType | **官方 QuotaType 仅 qps/concurrency/qpm/tpm**——查的是配额不是用量；传其他值虽 200 但全 0 无意义；不传默认 concurrency 全 0。时间范围建议 ≤7 天（文档明确） |
| `UsageMonitoring`（调用量查询，**这才是用量**） | 2025-05-21 | ProjectName + ResourceID + Start/End + **Mode=daily 必选**（漏了报 InvalidParameter） | **Mode=daily 是必选参数**（曾误判「参数不明」）；UsageType 用 **`audio_duration`**（时长包正确类型，**返回单位=小时**！不是秒），text_words/characters 也可用；返回按天 `{Day, Value, UsageType}` |

文档 ID：ResourcePacksStatus=1801938、QuotaMonitoring=1801956、UsageMonitoring=1801957、ListAPIKeys=1801323。抓取用 `r.jina.ai/https://docs.volcengine.com/docs/6561/<id>`（docs 域名 OK；www.volcengine.com 部分页面只返回侧边栏导航，正文缺失）。

## 二、资源 ID 三连坑（核心障碍）

1. **ResourceID/BlueprintID 必选，API 无法枚举账号资源**——ListAPIKeys（只返回 APIKey/Name/ID）、ServiceStatus（返回空实例）都不带资源信息。
2. 真实 ID 格式 `volc.service_type.XXXXX`（文档附录「服务唯一标识」），账号特定，示例 10029 查空。
3. **资源包实例号 ≠ ResourceID**：用户从控制台拿的 `SeedAudio1.02000000863924357890`（SeedAudio1.0 创作版-时长包30分钟，资源包实例号/`Packs[].InstanceNumber`）传入 RPS 返回 200 但 TotalCount=0、QM/UM 直接 500 InternalError。**500 是「服务端识别出格式但查无数据」的信号**，与示例 ID 的 200 空数据不同。
4. **✅ 真实 ResourceID 拿法（2026-08-11 终版）**：见第三节——借用户浏览器登录态调控制台内部 API `ListServiceTypes`（带 cookie `csrfToken` 的 X-CSRF-Token header），响应 `Items[].ResourceID` 是全量服务列表。本账号 seedaudio 真实 ID = **`volc.service_type.10074`**（Name=「创作版」、UsageType=audio_duration）。

## 三、控制台内部 API（绕过枚举死结——✅ 已跑通，唯一可靠拿 ResourceID 的路）

控制台前端（用户登录态）直接调内部代理 API，响应带真实资源数据。**这是 OpenAPI 无法枚举账号资源时的唯一解法**：

```
https://console.volcengine.com/api/top/speech_saas_prod/cn-north-1/2025-05-20/{ListServiceTypes | CountAllResourcePacks | ListProducts | GetProductCenterStruct | ListAPIKeys | DescribeAccountTags ...}
```

**跑通配方（2026-08-11 终版，commit dfa52c7）**：
1. 借用户浏览器登录态（Kimi WebBridge `find_tab active:true` 或新开 tab），导航到用量统计页 `https://console.volcengine.com/speech/new/usage-statistics?projectName=default`
2. evaluate 里 fetch（同源自动带 cookie），**CSRF token 的 cookie 名是精确的 `csrfToken`**：
   ```js
   const csrf = document.cookie.split(';').map(c=>c.trim()).find(c=>c.startsWith('csrfToken='))?.split('=')[1] || '';
   const h = {'Content-Type':'application/json', 'X-CSRF-Token': csrf};
   const r = await fetch('https://console.volcengine.com/api/top/speech_saas_prod/cn-north-1/2025-05-20/ListServiceTypes', {method:'POST', headers:h, body:'{}'});
   const j = await r.json();  // Result.Items[].ResourceID 全量服务列表
   ```
   ⚠️ 注意：cookie 名不是 `volc_csrf_token`/`csrf-token`，正则 `/csrf[^=]*/` 匹配出的值会报 InvalidCSRFToken——**必须精确匹配 `csrfToken=`**。
3. 从 Items 里按服务名找目标：seedaudio 1.0 对应 Name=「创作版」、UsageType=`audio_duration`、ResourceID=**`volc.service_type.10074`**（本账号实测；不同账号数字不同）
4. 其他有用 action：`CountAllResourcePacks`（资源包计数）、`ListAPIKeys`、`GetProductCenterStruct`

- 用量统计页 URL：`https://console.volcengine.com/speech/new/usage-statistics?projectName=default`；API Key 管理页：`/speech/new/setting/apikeys?projectName=default`。
- 商品服务下拉的选项「豆包音频生成模型1.0」= SeedAudio 1.0 的计费服务名。

## 四、Kimi WebBridge 操作火山控制台技巧（已验证）

- **借用户登录态**：`find_tab url=console.volcengine.com active:true` 直接借用户正看的标签页（borrowed:true），不用重新登录。
- **Arco 组件吃真实点击**：`.arco-cascader` 等 Arco Design 组件对 JS 合成事件（`el.click()`/dispatchEvent MouseEvent，isTrusted=false）**完全无反应**——必须用 WebBridge 的 `click` 工具（chrome.debugger 真实点击，isTrusted=true）。本会话选中下拉选项只能靠它。
- **找内部 API**：`network cmd=start`（不带 filter 抓全量）→ 操作页面 → `network cmd=list filter=console.volcengine.com` 过滤出内部 API URL；`detail` 需要 requestId 且**不保存响应体**（要看响应得用 evaluate fetch 或改用页面操作）。
- **Windows 调用姿势**：JSON 请求体用 python 写文件（shell heredoc/echo 会破坏中文/转义，skill 原话「corrupts non-ASCII」），`curl.exe -s --data-binary @file` 发送；evaluate 代码含 `\\n` 时同样会被 JSON 转义搞坏——用 python json.dump 生成请求体最稳。

## 五、结论状态（2026-08-11 终版，全部打通）

代码侧全部修对并部署 NAS（commit 16f0e17 + 6852da3 + **dfa52c7**，分支 v2.2-dual-panel）：/quota 三级兜底（资源包 → 近7天调用量时长 → 本地历史统计）。**真实 ResourceID 已拿到**（`volc.service_type.10074`，见第三节配方）+ Types 必传坑已修。实测余额：免费礼包 60分钟-已用14.64 + 创作版30分钟-未用 = **剩余 75.4 分钟**，/quota 返回 `balance_text: "剩余 75.4分钟"` 真实链路验证通过。`.env` 的 VOLC_RESOURCE_ID 已更新为 10074（NAS 端 .env.bak.20260811 为旧备份）。
