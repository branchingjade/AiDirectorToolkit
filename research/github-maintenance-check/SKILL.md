---
name: github-maintenance-check
description: 核查 GitHub 项目是否还在维护、对比活跃度。触发词：还在维护吗、推荐个软件。
category: research
version: 1.0.0
author: hermes
license: MIT
metadata:
  hermes:
    tags: [research, github, open-source, verification]
    related_skills: [web-fetch-fallbacks, sourced-web-research]
---

# GitHub 开源项目活跃度核查（github-maintenance-check）

## When to Use（适用场景）
- 用户要"推荐还在维护的 X"（软件/客户端/工具/TV 应用）
- 判断某项目是否停更、能不能推荐
- 对比两个开源项目谁更值得用（维护角度）

## 核心铁律：star 数会骗人，pushed_at 才是证据
BBLL 案例（2026-08 实测）：17.4k star 的 B 站 TV 客户端，2025-02-28 后零提交 = 死项目；B 站 API 一改就集体失效，贴吧已在问"都用不了了"。**推荐前必须用 GitHub API 逐个验证，不许只看 star 数或搜索引擎描述**——"还在维护"是时效性结论，必须以最后提交时间为证据。

## 核查流程（全用 curl，免 key，60 次/时限额够用）

### 1. 批量查仓库存活状态
```bash
for repo in owner/repo1 owner/repo2; do
  curl -s "https://api.github.com/repos/$repo" | python3 -c "import json,sys; d=json.load(sys.stdin); print('stars:', d.get('stargazers_count'), '| archived:', d.get('archived'), '| pushed:', d.get('pushed_at')); print('desc:', (d.get('description') or '')[:110])"
done
```
判读：
- `pushed_at` = 最后提交时间。**近 1-2 个月有提交才算"还在维护"**；停更 >6 个月直接排除（API 一改就废的客户端类尤甚）。
- `archived: true` = 已归档，**即使 pushed 时间新也不能推**（归档后不可能再更新）。
- 返回 `full_name: None` = 仓库不存在/被删/DMCA——别在搜索结果里继续推它。

### 2. 查版本发布节奏（"稳定维护"的判据）
```bash
curl -s "https://api.github.com/repos/owner/repo/releases?per_page=10" | python3 -c "import json,sys; rs=json.load(sys.stdin); [print(r['tag_name'], '|', r['published_at'][:10]) for r in rs]"
```
稳定维护 = 近 1-2 月有版本 + 节奏可预测（如每周一版）。版本号阶段也透露成熟度：v0.9.x 还在功能大改 vs v1.6.x 稳定迭代。

### 3. 读 README / release notes（raw.githubusercontent 被墙时的替代）
`raw.githubusercontent.com` 墙内经常超时，直接用 GitHub API readme 端点（详见 web-fetch-fallbacks §7）：
```bash
curl -sL -H "Accept: application/vnd.github.raw" "https://api.github.com/repos/owner/repo/readme"
```
README 简略时（BT 案例：README 仅 358 字节），功能全在 release body 里，抓最近 3 个 release 的 body 扒功能清单：
```bash
curl -s "https://api.github.com/repos/owner/repo/releases?per_page=3" | python3 -c "import json,sys; [print('---', r['tag_name'], r['published_at'][:10], '---\n', (r.get('body') or '')[:600]) for r in json.load(sys.stdin)]"
```

### 4. 结论格式（用户习惯：证据表格 + 明确排除项）
- 表格呈现：项目 / 最后更新 / star / 特点，每行标注最后提交日期作证据
- 单独列"排除项 + 排除原因"（停更/归档/大陆不可用）——比只给推荐更可信
- 大陆可用性必须单独标注（如 aaa1115910/bv 原版 README 自述"不能在大陆用"）
- 推荐语给"适合谁"的选型指引（老设备/功能偏好），让用户自己定

## 陷阱
- 搜索结果里的"2025 年推荐"文章可能已经过时——文章发布日 ≠ 项目存活日，一律以 API 实况为准。
- 收集型仓库（如 oldsento/bilibili-client-software-collection）是发现候选的捷径，README 常带更新日期，先看它再逐个验证。
- 第三方客户端类项目共同风险：个人封装官方 API，官方一收紧就集体失效——"近 2 个月还在更新"比功能全更重要，推荐时明说这个风险。
- web_extract 在 extract_backend 为空时不可用（ddgs 是纯搜索后端），抓页面直接 curl。

## 参考
- references/bilibili-tv-clients-2026-08.md — B 站 TV 客户端生态盘点（2026-08 GitHub API 实测数据，含活跃/排除清单）
