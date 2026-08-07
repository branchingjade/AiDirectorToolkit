# Llama.cpp 集成 setup

> 来源：blender_mcp 官方 Wiki 页 `Llama.cpp`，作者 Dalai Felinto，最后更新 2026-04-24。

## 概述

Llama.cpp 是免费开源命令行 LLM 客户端，可在本地运行模型。blender_mcp 原生支持 Llama.cpp 作为 MCP 客户端。

## 前置条件

1. **Llama.cpp** >= build 8218
2. **支持 MCP tools + 代码生成的模型**（GGUF 格式）

## 安装 Llama.cpp

```bash
# Windows
winget install llama.cpp

# macOS / Linux
brew install llama.cpp
```

## 推荐模型

| 模型 | 下载 |
|------|------|
| Gemma4-26B-A4B | https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF |
| Qwen3.6-35B-A3B | https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF |

M3 MacBook 实测可用的量化文件：
- `gemma-4-26B-A4B-it-MXFP4_MOE.gguf`
- `Qwen3.6-35B-A3B-Q5_K_M.gguf`

⚠️ 需根据实际硬件选择适合的量化级别。

## MCP Server 安装

### Windows
```powershell
cd c:\
git clone https://projects.blender.org/lab/blender_mcp.git
```

### macOS / Linux
```bash
cd $HOME
git clone https://projects.blender.org/lab/blender_mcp.git
```

## 启动

### 1. 启动 llama-server
```bash
llama-server -m <MODELFILE.gguf>
# 可选：让 llama.cpp 自动下载模型
# llama-server --hf-repo unsloth/gemma-4-26B-A4B-it-GGUF --hf-file gemma-4-26B-A4B-it-MXFP4_MOE.gguf
```

### 2. 启动 blender-mcp HTTP 模式
```bash
# Windows
uv --directory C:\blender_mcp\mcp run blender-mcp --transport http --port 9191

# macOS / Linux
uv --directory $HOME/blender_mcp/mcp run blender-mcp --transport http --port 9191
```

### 3. 配置 Llama.cpp Web UI
1. 打开 `http://127.0.0.1:8080/`
2. 点击 "MCP Servers" → "+ Add new Server"
3. Server URL: `http://127.0.0.1:9191/`
4. 点击 Add → Save settings

配置完成后在 MCP Servers 列表中应看到 `blender-mcp`。

## 注意事项

- BLENDER_MCP 需要先启动并运行 Blender（插件需启用并监听端口 9876）
- llama-server 端口默认 8080，blender-mcp HTTP 默认 9191
- Wiki 中 Mac/Linux 的 `--transport` 参数有笔误（`http` 而非 `http`），以 `--transport http` 为准
- 可选使用 `--hf-repo` + `--hf-file` 让 llama.cpp 自动从 HuggingFace 下载模型
