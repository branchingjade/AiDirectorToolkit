# Memory Provider 对比明细（2026-08-14 查证）

## OpenViking（字节跳动 volcengine）

- 定位：AI Agent 上下文数据库，`viking://` 文件系统范式统一管理记忆/资源/技能；内容写入生成 L0 摘要/L1 概览/L2 详情三层，按需加载；检索留轨迹可调试
- 许可证：**AGPL-3.0**（LICENSE 为标准 AGPL v3 文本）
  - 商用场景细分：内部使用（含改源码）= 自由；不改代码直接部署对外服务 = 自由；**改了源码 + 对外提供网络服务（SaaS/托管）= 修改后全部源码必须以 AGPL-3.0 开源回吐**（Section 13，AGPL 招牌条款）；衍生作品同协议授权
  - 一句话：内部用随便改，改成收费 SaaS 必须开源
- Hermes 集成：**官方已内置 provider v2.0.0**（`<hermes-agent>/plugins/memory/openviking/`，plugin.yaml: version 2.0.0, hooks: on_session_end, pip 依赖仅 httpx）——改 `memory.provider: openviking` 一行即切，零安装
- 来源：https://github.com/volcengine/OpenViking （LICENSE / README_CN.md）

## TencentDB Agent Memory（腾讯，TDB）

- 定位：团队级记忆中心，4 层语义金字塔 **L0 对话 → L1 原子事实 → L2 场景块 → L3 用户画像（Persona）**；短期记忆符号化（Mermaid 画布 + node_id 回溯，重日志卸载到 refs/*.md）
- 许可证：**MIT**（LICENSE 开头原文 "TencentDB Agent Memory is licensed under the MIT"）——随便用/改/闭源商用，唯一义务=保留版权声明
- 部署：本地 **SQLite + sqlite-vec** 后端，不强制上腾讯云；LLM 可接任意 OpenAI 兼容端点（TDAI_LLM_* 环境变量，默认指腾讯云 LKE）
- 厂商基准（自报，WideSearch/SWE-bench 编程长任务场景）：token -61.38%、通过率 +51.52%（WideSearch）；SWE-bench token -33.09%；PersonaMem 画像准确率 48%→76%
- Hermes 集成：第三方插件 `memory_tencentdb`（plugin.yaml: hooks on_memory_write/on_session_end，别名 tdai / memory-tencentdb）；独立 Node Gateway sidecar（:8420，capture/search/recall HTTP 接口，可配 Bearer 鉴权 TDAI_GATEWAY_API_KEY）
- 安装要求：Node ≥ 22.16、npm；Windows 有 `setup-hermes-memory-tencentdb.bat`（检查 node/npm/Python/Hermes，npm install 依赖，复制插件到 `%HERMES_HOME%\plugins\memory_tencentdb`，写环境变量到 `%HERMES_HOME%\.env`，启动 Gateway 并轮询 /health）
- 来源：https://github.com/TencentCloud/TencentDB-Agent-Memory （README / README_CN.md / LICENSE）

## Hindsight（本机现用，2026-08 启用）

- Hermes 官方内置 provider v1.0.0（`plugins/memory/hindsight/`，pip 依赖 hindsight-client>=0.6.1）
- 知识图谱 + 实体解析 + 多策略检索；`memory.provider: hindsight` 已全面启用，桌面+飞书链路均验证通过
- 已知边界：单 bank（bank_id=hermes）无成员维度隔离；recall 是模糊语义召回，替代不了确定性查找；consolidation 依赖 DeepSeek

## 本机兼容性实测（2026-08-14，TDB 只查未装）

| 检查项 | 结果 |
|---|---|
| Node | v22.23.2 ✅（要求 ≥22.16） |
| npm | 12.0.2 ✅ |
| 端口 8420 | 空闲 ✅ |
| 插件扫描 | `$HERMES_HOME/plugins/<name>/`，与 bat 输出路径一致 ✅ |
| 唯一坑 | bat 默认 `HERMES_HOME=%USERPROFILE%\.hermes`；本机实际 = `C:\Users\HMSJ\AppData\Local\hermes`，必须先 `$env:HERMES_HOME=...` 再跑，否则装错目录 Hermes 扫不到 |

## 评估结论样板（2026-08-14 给用户）

现状无痛点 → 不值得换。TDB/OpenViking 均为已验证可用备胎，触发条件（Hindsight recall 质量问题 / 做商业产品要许可证 / token 成本压力）出现时两条路都有现成接入方案。
