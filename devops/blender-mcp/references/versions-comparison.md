# blender_mcp 官方版 vs 社区版 详细对比

## 基本信息

| 维度 | 官方版 | 社区版 |
|------|--------|--------|
| 仓库 | `lab/blender_mcp` (Blender Gitea) | `ahujasid/blender-mcp` (GitHub) |
| 维护者 | Dalai Felinto（Blender 基金会，UI 模块负责人） | Siddharth Ahuja |
| 许可证 | GPL-3.0-or-later | MIT |
| Stars | 18 | — |
| Open Issues | 14 | — |
| 语言 | Python | Python |
| 创建时间 | 2026-02-21 | 2025 |

## 发布历史

### 官方版

| 版本 | 日期 | 类型 | 说明 |
|------|------|------|------|
| v1.0.0 | 2026-04-27 | 正式版 | Initial release |
| v0.3.0 | 2026-04-14 | 预发布 | Updated MCPB |
| 26.04.10 | 2026-04-10 | 预发布 | Initial MCPB Package |
| v0.1.0 | 2026-03-24 | 预发布 | Basic MCP functionality |

v1.0.0 资产：
- `mcp-1.0.0.zip` (16KB) — MCP Server，189,069 次下载
- `blender-1.0.0.mcpb` (5.5MB) — Blender 插件包，13,389 次下载

### 社区版

PyPI 包 `blender-mcp` v1.6.4，月下载 ~28,000。

## 架构对比

```
官方版：
  MCP Client ⇐ MCP/stdio ⇒ blender-mcp (FastMCP) ⇐ TCP socket(9876) ⇒ Blender Addon (blender_mcp_addon)

社区版：
  MCP Client ⇐ MCP/stdio ⇒ blender-mcp (FastMCP) ⇐ TCP socket(9876) ⇒ Blender Addon (addon.py)
```

两者架构几乎相同，都是 FastMCP + TCP socket + Blender addon。差异在于 Python 包名和插件名。

## 功能矩阵

| 功能 | 官方版 | 社区版 |
|------|:---:|:---:|
| execute_blender_code | ✅ | ✅ |
| 场景分析（对象/层级） | ✅ | ✅ |
| Blender API 文档查询 | ✅ | ❌ |
| 用户手册查询 | ✅ | ❌ |
| 窗口/区域截图 | ✅ | ✅ |
| 视口/缩略图渲染 | ✅ | ✅ |
| 导航（跳转工作区/物体） | ✅ | ❌ |
| Poly Haven 资产 | ❌ | ✅ |
| Hyper3D/Rodin 文生3D | ❌ | ✅ |
| Hunyuan3D | ❌ | ✅ |
| Sketchfab 导入 | ❌ | ✅ |
| 材质编辑助手 | ❌ | ✅ |
| 场景清理 | ❌ | ✅ |
| 后台无头 Blender | ✅ | ❌ |
| Llama.cpp HTTP 传输 | ✅ | ❌ |
| CLI 聊天客户端 | ✅ | ❌ |
| 内置 telemetry | ❌ | ✅ |

## 依赖对比

### 官方版
```
mcp[cli]>=1.2.0
docutils
pyyaml
```

### 社区版
```
mcp[cli]>=1.3.0
httpx>=0.27.0
```
