# 网页调研常见障碍与应对

> 撰写 analysis-report 时，网页调研经常遇到以下障碍，按优先级排列应对策略。

## 一、搜索引擎封锁

**现象**：
- Google → CAPTCHA（`sorry/index` 重定向）
- Bing → Cloudflare 验证（"请解决以下难题以继续"）
- DuckDuckGo → CAPTCHA（"Select all squares containing a duck"）

**应对**：
1. **跳过搜索，直接访问已知产品页**（最有效）。如 BytePlus 产品页 `byteplus.com/en/product/xxx` 直接用 curl 验证存在性。
2. 用 **浏览器工具导航到搜索页** 有时能绕过（Bing 偶尔成功），但不是可靠方案。
3. 对于中文搜索，Bing 对中文关键词匹配差——"火山引擎 视频超分"返回的是真·火山科普页面。此时**英文搜索或直接用产品域名推测 URL**。

## 二、SPA 页面无法提取内容

**现象**：
- curl 返回 HTTP 200 + JS 壳（`You need to enable JavaScript to run this app`）
- browser 工具渲染为空页面或 SPA 路由 404

**涉及平台**：
- volcengine.com（火山引擎）—— 所有产品页为 React SPA
- byteplus.com（BytePlus）—— 同上
- docs.byteplus.com —— 同上
- openai.com —— Cloudflare 保护

**应对**：
1. curl 返回 200 只代表「页面存在」，不代表「内容可提取」
2. browser 工具对这些 SPA 的渲染不稳定：higgsfield.ai 正常，volcengine/byteplus 空白或 404
3. **标记为「需本地浏览器打开」**，把链接给用户自己看
4. 尝试 docs 子域名——有时文档站比产品站更容易渲染

## 三、数据来源分级

报告中必须标明每项数据的来源级别：

| 级别 | 含义 | 示例 |
|---|---|---|
| 网页验证 | curl/browser 成功提取 | "Topaz $299/年（topazlabs.com 价格页验证）" |
| 训练知识 | 模型记忆，可能过时 | "CapCut Pro ¥79/月（训练数据，待验证）" |
| 推断 | 基于已知信息推导 | "火山引擎 智能超分 API（基于产品名录推断，未访问具体页）" |

## 四、GitHub API 作为搜索引擎替代方案

当搜索被 CAPTCHA 封锁时，GitHub API 是发现**开源工具**的最佳替代方案——而且数据（stars、推送日期、许可证、描述）比二手博客更可靠。

### 基础用法

```bash
curl -s "https://api.github.com/search/repositories?q=voice+conversion&sort=stars&order=desc&per_page=15" \
  | python3 -c "
import json,sys
data = json.load(sys.stdin)
for i in data['items']:
    print(f\"{i['stargazers_count']:>6} ⭐ | {i['name']:<45s} | {i['description'][:120] if i['description'] else 'N/A'} | pushed: {i['pushed_at'][:10]}\")
"
```

### 查询技巧

| 目标 | Query | 参数 |
|------|-------|------|
| 通用工具发现 | `key+terms`（AND 默认） | `sort=stars&order=desc` |
| 零样本/近期 | `zero-shot+voice+conversion` | 同上 |
| 特定功能 | `voice+conversion+real-time` | 同上 |
| 分页控制 | - | `&per_page=100`（最大） |

### 提取仓库详情

```bash
# 读取 README（判断工具是否真的适合场景）
curl -s "https://api.github.com/repos/<owner>/<repo>/readme" \
  | python3 -c "import json,sys,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode('utf-8')[:3000])"
```

### 关键数据字段

| 字段 | 含义 | 评估标准 |
|------|------|---------|
| `stargazers_count` | 社区认可度 | >5k = 成熟广泛使用；1-5k = 活跃小众；<1k = 早期/小众 |
| `pushed_at` | 维护活跃度 | 数月内有更新 = 健康；>1年 = 可能已停维 |
| `license.spdx_id` | 许可证 | MIT/Apache = 宽松；GPL/AGPL = 传染性；缺少 = 风险 |
| `archived` | 归档标记 | true = 已死，慎用 |
| `open_issues_count` | 未解决问题 | 相对 stars 比例过高 = 维护不足 |

### 限流

| 认证 | 限额 | 说明 |
|------|------|------|
| 未认证 | 60 次/小时 | 轻度调研够用 |
| 带 Token | 5000 次/小时 | 大规模搜索时设置 `GITHUB_TOKEN` |

### 适用场景

- 搜索/商业搜索引擎全部被 CAPTCHA 封锁时（本会话中 Google、DuckDuckGo、Bing 全部被封）
- 需要客观的项目活跃度数据（stars、推送时间、许可证）
- 需要批量对比多个工具的社区成熟度

### 局限

- 仅覆盖 GitHub 上的项目（GitLab/Bitbucket/自建仓库不可见）
- 不反映商业/闭源产品
- Stars 可能有水分，需结合 `pushed_at` 和 README 质量判断

## 五、2026-06 已知可访问的产品页
| 平台 | URL | 状态 |
|---|---|---|
| Topaz Video AI | `topazlabs.com` | ✅ curl 可提取文字 |
| Higgsfield AI | `higgsfield.ai` | ✅ browser 渲染正常 |
| BytePlus Video Enhancer | `byteplus.com/en/product/video-enhancer` | ⚠️ curl 200，browser 渲染 404 |
| BytePlus Video Enhance Docs | `docs.byteplus.com/en/docs/byteplus-video-enhance` | ⚠️ curl 200，browser 空白 |
| 火山引擎产品页 | `volcengine.com/product` | ⚠️ browser 空白 |
| OpenAI Sora | `openai.com/sora/` | ❌ Cloudflare 保护 |
| RunningHub | `runninghub.ai` | ✅ curl 可提取 |
