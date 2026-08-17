---
name: hermes-memory-provider-selection
description: 评估/对比/切换 Hermes 记忆提供方（memory provider）时用。
version: 1.0.0
author: curator
license: MIT
metadata:
  hermes:
    tags: [devops, hermes, memory, provider-selection]
    related_skills: [hindsight-memory-ops, hermes-provider-integration]
---

# Hermes 记忆提供方选型与迁移评估

## When to Use

评估"要不要换掉现在的记忆方案"这一类任务的标准流程。触发词：记忆方案对比、换记忆、memory provider、OpenViking、TencentDB、TDB、商用范围。用户问某记忆系统/上下文数据库怎么样、商用范围、值不值得换时用。

## 一、先看官方内置，避免重复评估

Hermes memory provider 插件机制（2026-08 查证，`agent/memory_provider.py` + `plugins/memory/__init__.py`）：
- **内置（bundled）**：`<hermes-agent>/plugins/memory/<name>/`，当前含 hindsight、openviking(v2.0.0)、mem0、honcho、byterover、holographic、retaindb、supermemory
- **用户安装**：`$HERMES_HOME/plugins/<name>/`，同名冲突时内置优先
- 同一时间**只有一个 provider 激活**，由 `memory.provider` 配置决定——切换=改一行配置，内置 provider 零安装成本
- 评估任何第三方 provider 前先 `ls plugins/memory/` 确认官方是否已内置（2026-08 就发现 openviking 早已内置，差点白评估）

## 二、决策框架：什么时候才值得换

三个触发信号，没触发就不换（用户偏好最小必要实现，多一个 sidecar 进程/密钥配置本身就是反对理由）：
1. 现有 provider 出现**实际 recall 质量问题**（搜不到该记的东西）且无法调优
2. 要把记忆能力做成**对外商业产品**（许可证差异才真正重要）
3. 长任务 **token 成本**成为真实账单压力（订阅制计费场景此条自动失效）

换的方案必须包含：现有记忆 bank 数据**不自动迁移**（断档成本）、新 provider 的运维负担（额外进程/依赖）、与用户已有工作流（如 Obsidian 画像体系）是否重复。

## 三、兼容性验证流程（只查不改）

评估第三方 provider 本机可装性，用户同意后才做，全程不改配置：
1. 读 `config.yaml` 的 `memory.provider`（当前值）
2. `ls <hermes-agent>/plugins/memory/` 看官方已内置哪些
3. 抓安装脚本，**核对它假设的 HERMES_HOME/插件目标路径 vs 实际路径**——本机 HERMES_HOME=`C:\Users\HMSJ\AppData\Local\hermes`，不是 `~/.hermes`（`~/.hermes` 是空壳，只有 `custom_providers: []`）；多数第三方脚本默认 `%USERPROFILE%\.hermes`，直接跑会装错目录 Hermes 根本扫不到
4. `netstat -ano | grep :<端口>` 查 sidecar 端口占用
5. `node --version` / `npm --version` 对照要求
6. 输出=环境门槛表 + 决策建议，不改任何配置

验证 Hermes 实际 home 目录：`python -c "import sys; sys.path.insert(0,'<hermes-agent路径>'); from hermes_constants import get_hermes_home; print(get_hermes_home())"`

## 四、已评估 provider 速查（2026-08-14 本机实测）

| 项目 | OpenViking（字节） | TencentDB Agent Memory（腾讯） | Hindsight（现用） |
|---|---|---|---|
| 许可证 | AGPL-3.0（改后对外网络服务须整体开源回吐） | MIT（随便商用，保留版权声明即可） | Hermes 内置 |
| 部署 | 本地 | 本地 SQLite+sqlite-vec，不强制上腾讯云 | 本地+外部服务 |
| Hermes 集成 | **官方内置 provider v2.0.0**，改 `memory.provider` 即切 | 第三方插件 `memory_tencentdb`，Node sidecar gateway :8420 | 官方内置，已全面启用 |
| 安装门槛 | 零 | Node≥22.16 + npm + `TDAI_LLM_*` 环境变量 + bat 脚本（HERMES_HOME 要手动指路） | — |
| 卖点 | 上下文文件系统 viking://，L0/L1/L2 分层 | L0→L3 语义金字塔含用户画像层，长任务 token -61%（厂商自报） | 已稳定运行 |

详细对比与来源见 `references/provider-comparison.md`。

## 五、坑（2026-08-14 实测）

- 第三方 Hermes 集成脚本（TDB 的 `setup-hermes-memory-tencentdb.bat`）默认 `HERMES_HOME=%USERPROFILE%\.hermes`——本机必须 `$env:HERMES_HOME="C:\Users\HMSJ\AppData\Local\hermes"` 后再跑
- 厂商基准数据（token 节省/通过率提升）是自报，且场景多为编程长任务（SWE-bench/WideSearch），与创作/运维场景相关度有限；订阅制计费下省 token 不省钱
- 评估结论要诚实区分"环境门槛过了"和"值得换"——两者独立
